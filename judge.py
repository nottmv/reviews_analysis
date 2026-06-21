from llm_client import get_model, make_client
from prompts import JUDGE_PROMPT
from schema import JudgeVerdict
import json

client = make_client()
MODEL = get_model()

def judge_answer(question: str, answer: str, sources: list[str]) -> JudgeVerdict:
    evidence = f"Вопрос: {question}\nОтвет: {answer}\nЦитаты:\n" + "\n".join(sources)
    return client.chat.completions.create(
        model=MODEL,
        response_model=JudgeVerdict,
        max_retries=3,
        temperature=0.0,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": evidence},
        ],
    )