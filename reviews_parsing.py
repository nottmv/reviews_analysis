from google_play_scraper import Sort, reviews
import csv
from datetime import datetime, timedelta

PACKAGE_NAME = "com.uma.musicvk"
cutoff_date = datetime.now() - timedelta(days=90)  # наивная дата (без tzinfo)

print("⏳ Собираю отзывы...")
result, _ = reviews(
    PACKAGE_NAME,
    lang='ru',
    country='ru',
    sort=Sort.NEWEST,
    count=200  # можно увеличить, но не более ~200 за раз
)

# Фильтруем: убираем временную зону у каждого review['at']
filtered_reviews = [
    review for review in result
    if review['at'] and review['at'].replace(tzinfo=None) > cutoff_date
]

print(f"✅ Всего получено: {len(result)} отзывов")
print(f"✅ За последние 90 дней: {len(filtered_reviews)} отзывов")

# Сохраняем в CSV
with open('vk_music.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['rating', 'content', 'userName', 'at', 'reviewCreatedVersion'])
    for review in filtered_reviews:
        writer.writerow([
            review['score'],
            review['content'],
            review['userName'],
            review['at'],
            review['reviewCreatedVersion']
        ])