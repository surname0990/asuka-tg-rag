import psycopg2
import logging
from contextlib import closing

class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.connection = self.connect()

    def connect(self):
        """Подключение к базе данных."""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            logging.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def save_document(self, tg_id, chat_id, timestamp, text):
        """Сохранение документа и его метаданных в базе данных."""
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("""
                    INSERT INTO documents (tg_id, chat_id, timestamp, text) 
                    VALUES (%s, %s, %s, %s)
                """, (tg_id, chat_id, timestamp, text))
                self.connection.commit()
                logging.info(f"Сохранён документ в БД: {text}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении документа: {e}")

    def load_knowledge_base(self):
        """Загрузка документов из базы данных."""
        documents = []
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("SELECT text FROM documents")
                rows = cursor.fetchall()
                for row in rows:
                    documents.append(row[0])
        except Exception as e:
            logging.error(f"Ошибка при загрузке базы знаний: {e}")
        return documents

    def close(self):
        """Закрытие подключения к базе данных."""
        if self.connection:
            self.connection.close()
            logging.info("Подключение к базе данных закрыто.")
