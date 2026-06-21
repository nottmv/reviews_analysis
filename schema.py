"""
schema.py — Модели для маркетингового анализа отзывов
====================================================
Адаптированы под отзывы на приложения (Звук, Яндекс Музыка, ВК Музыка).
Техники: IE, аспектный анализ, LLM-as-Judge, агент с инструментом.
"""

from __future__ import annotations
from typing import Literal, Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator


# ---------- Базовые сущности ----------
class Review(BaseModel):
    """Один отзыв из CSV."""
    product: str
    review_text: str
    rating: int = Field(ge=1, le=5)
    review_date: date
    user_name: Optional[str] = None

    @field_validator("review_date")
    @classmethod
    def date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError(f"Дата {v} не может быть в будущем")
        return v


# ---------- Аспектный анализ ----------
ASPECTS = Literal[
    "sound_quality",   # качество звука
    "ui_design",       # интерфейс, дизайн
    "price",           # цена, подписка
    "ads",             # реклама
    "recommendations", # рекомендации, плейлисты
    "stability",       # стабильность, баги
    "speed",           # скорость работы
    "support"          # поддержка, обратная связь
]

class AspectSentiment(BaseModel):
    aspect: ASPECTS
    sentiment: Literal["positive", "negative", "neutral"]
    quote: str
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("quote")
    @classmethod
    def quote_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Цитата не может быть пустой")
        return v


class ProductAnalysis(BaseModel):
    product: str
    aspects: list[AspectSentiment]
    summary: str = ""


# ---------- Агент: сравнение продуктов ----------
class CompareRequest(BaseModel):
    product_a: str
    product_b: str
    aspect_filter: Optional[list[str]] = None   # если нужно сравнить только по определённым аспектам


class CompareResult(BaseModel):
    product_a: str
    product_b: str
    comparison: str                             # текстовое сравнение
    winner: Optional[str] = None                # какой продукт лучше (или "ничья")


# ---------- Judge ----------
class JudgeVerdict(BaseModel):
    ok: bool
    reason: str
    hallucinations: bool = False
    ghost_quotes: bool = False


class FinalAnswer(BaseModel):
    question: str
    answer: str
    sources: list[str]          # цитаты из отзывов, на которых основан ответ
    verdict: JudgeVerdict

class AspectListWrapper(BaseModel):
    aspects: list[AspectSentiment]