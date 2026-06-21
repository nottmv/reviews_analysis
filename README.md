# Маркетинговый аналитик по отзывам на музыкальные приложения

Система отвечает на вопросы о продуктах на основе отзывов пользователей.

## Запуск
1. Установите зависимости: `pip install -r requirements.txt`
2. Создайте `.env` с переменными `LLM_BASE_URL`, `LLM_AUTH_TOKEN`, `LLM_MODEL` (см. `.env.example`)
3. Поместите CSV с отзывами в папку `input/` (zvuk.csv, yandex_music.csv, vk_music.csv)
4. Задайте вопрос: `python pipeline.py --question "Почему пользователи недовольны качеством звука у Звука?"`
5. Для оценки: `python eval.py`

## Структура
- `input/` - исходные CSV с отзывами
- `output/` - результаты прогона (eval_results.json, summary.json)
- `pipeline.py` - основной пайплайн
- `rag.py` - индексация и retrieval
- `agent.py` - инструмент сравнения
- `judge.py` - проверка ответов
- `schema.py` - модели данных
- `prompts.py` - промпты
- `eval.py` - оценка на 15 вопросах
- `gold.json` - тестовые вопросы
- `отчет.md` - финальный отчёт