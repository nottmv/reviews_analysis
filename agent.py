from llm_client import get_model, make_client
from schema import CompareRequest, CompareResult
from prompts import COMPARE_PROMPT
from rag import load_reviews, build_index, retrieve
import json

client = make_client()
MODEL = get_model()

# Предзагружаем корпус и индекс при старте
REVIEWS = load_reviews(["input/zvuk.csv", "input/yandex_music.csv", "input/vk_music.csv"])
MODEL, EMBEDDINGS = build_index(REVIEWS)

def compare_products(request: CompareRequest) -> CompareResult:
    """Инструмент сравнения двух продуктов."""
    # Извлекаем релевантные отзывы по каждому продукту
    rev_a = retrieve(request.product_a, MODEL, EMBEDDINGS, REVIEWS, top_k=10)
    rev_b = retrieve(request.product_b, MODEL, EMBEDDINGS, REVIEWS, top_k=10)

    # Извлекаем аспекты (здесь можно использовать extract_aspects из pipeline, 
    # но для простоты просто передаём тексты)
    context_a = "\n".join([r["review_text"] for r in rev_a])
    context_b = "\n".join([r["review_text"] for r in rev_b])

    prompt = COMPARE_PROMPT.format(product_a=request.product_a, product_b=request.product_b)
    user_msg = f"Отзывы на {request.product_a}:\n{context_a}\n\nОтзывы на {request.product_b}:\n{context_b}"

    result = client.chat.completions.create(
        model=MODEL,
        response_model=CompareResult,
        max_retries=2,
        temperature=0.0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_msg},
        ],
    )
    return result