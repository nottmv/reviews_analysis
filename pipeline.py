import argparse
import json
from rag import load_reviews, build_index, retrieve
from schema import AspectSentiment, ProductAnalysis, AspectListWrapper
from judge import judge_answer
from agent import compare_products, CompareRequest
from llm_client import make_client, get_model
from prompts import EXTRACT_ASPECTS_PROMPT

client = make_client()
MODEL = get_model()


def extract_aspects_batch(reviews_text: str) -> list[AspectSentiment]:
    """Извлекает аспекты сразу из всех переданных отзывов (один вызов LLM)."""
    prompt = EXTRACT_ASPECTS_PROMPT + "\n\n" + reviews_text
    resp = client.chat.completions.create(
        model=MODEL,
        response_model=AspectListWrapper,
        max_retries=2,
        temperature=0.0,
        messages=[
            {"role": "system", "content": "Ты — анализатор отзывов. Верни JSON по схеме."},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.aspects


def analyze(question: str, reviews: list[dict], model, embeddings) -> dict:
    # 1. RAG: получаем top_k отзывов
    top_reviews = retrieve(question, model, embeddings, reviews, top_k=5)  # уменьшили до 5

    # 2. Объединяем тексты отзывов в один блок и извлекаем аспекты за один вызов
    combined = "\n---\n".join(r["review_text"] for r in top_reviews)
    aspects = extract_aspects_batch(combined)

    # 3. Собираем ответ и цитаты
    quotes = [a.quote for a in aspects]
    answer_lines = [f"[{a.aspect}] {a.sentiment}: {a.quote}" for a in aspects]
    answer = "\n".join(answer_lines)

    # 4. Judge
    verdict = judge_answer(question, answer, quotes)


    # Определяем, какие инструменты использовались
    tools_used = ["rag", "extract_aspects_batch"]
    if any(word in question.lower() for word in ["сравни", "vs"]):
        tools_used.append("compare_products")
    tools_used.append("judge")

    return {
        "question": question,
        "answer": answer,
        "sources": quotes,
        "verdict": verdict.model_dump(),
        "tools_used": tools_used,
        "steps": len(tools_used)  # число LLM-вызовов
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True, help="Вопрос к системе")
    args = parser.parse_args()

    reviews = load_reviews(["input/zvuk.csv", "input/yandex_music.csv", "input/vk_music.csv"])
    model, embeddings = build_index(reviews)
    result = analyze(args.question, reviews, model, embeddings)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()