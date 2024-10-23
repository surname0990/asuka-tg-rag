# Asuka - AI Bot

Knowledge Bot — это Telegram-бот, использующий нейронные сети для использования документации в проектах по разработке, а также техподдержке.

*Ссылается на Asuka Kazama, добавляя нотку силы и уверенности в помощи с документацией. 

## Особенности

- Добавление документов в базу данных.
- Хранение метаданных о документах (данных).
- Генерация ответов на запросы с использованием OpenAI.
- Использование векторной базы данных для быстрого поиска.

## Технологии

- Python
- PostgreSQL
- Telegram API
- OpenAI API
- FAISS
- Sentence Transformers

## Установка

### Установите необходимые библиотеки:

```bash
pip install -r requirements.txt
```

1. Клонируйте репозиторий:

```
git clone https://github.com/yourusername/knowledge-bot.git
```
```
cd knowledge-bot
```
2.  Настройте базу данных PostgreSQL. Вы можете использовать Docker для создания контейнера PostgreSQL:

```
docker run --name my_postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=postgres -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgres
```

Подключитесь к контейнеру и создайте необходимые таблицы:
```
docker exec -it my_postgres psql -U postgres -d mydatabase
```
Выполните следующий SQL-код для создания таблиц:

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id VARCHAR(255) UNIQUE NOT NULL,
    position VARCHAR(255) NOT NULL,
    project VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    text TEXT NOT NULL
);
```

3. Поправьте config.json

4. Запустите
```
python main.py
```
