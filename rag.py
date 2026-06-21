import csv
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def load_reviews(csv_paths: list[str]) -> list[dict]:
    """Загружает все CSV, добавляет поле product из имени файла."""
    reviews = []
    for path in csv_paths:
        product_name = path.split("/")[-1].replace(".csv", "")
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                reviews.append({
                    "product": product_name,
                    "review_text": row["content"],
                    "rating": int(row["rating"]),
                    "date": row["at"][:10],
                    "user": row.get("userName", "")
                })
    return reviews

def build_index(reviews: list[dict]):
    """Строит эмбеддинги для всех отзывов."""
    model = SentenceTransformer(MODEL_NAME)
    texts = [r["review_text"] for r in reviews]
    print(f"Эмбеддинг {len(texts)} отзывов...")
    start = time.time()
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"Готово за {time.time() - start:.1f} с")
    return model, np.array(embeddings)

def retrieve(query: str, model, embeddings, reviews, top_k=5):
    """Возвращает top_k отзывов, наиболее близких к запросу."""
    q_emb = model.encode([query])
    sims = cosine_similarity(q_emb, embeddings)[0]
    top_idx = np.argsort(sims)[::-1][:top_k]
    return [reviews[i] for i in top_idx]