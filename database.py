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

    def save_document(self, tg_id, chat_id, timestamp, text, group_id):
        """Сохранение документа и его метаданных в базе данных."""
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("""
                    INSERT INTO documents (tg_id, chat_id, timestamp, text, group_id) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (tg_id, chat_id, timestamp, text, group_id))
                self.connection.commit()
                logging.info(f"Сохранён документ в БД: {text}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении документа: {e}")

    def load_knowledge_base(self, group_id):
        """Загрузка документов из базы данных для указанной группы."""
        documents = []
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("SELECT text FROM documents WHERE group_id = %s", (group_id,))
                rows = cursor.fetchall()
                for row in rows:
                    documents.append(row[0])
        except Exception as e:
            logging.error(f"Ошибка при загрузке базы знаний для группы {group_id}: {e}")
        return documents

    def add_user_to_group(self, group_id, user_id):
        """Добавление пользователя в группу, если он не добавлен ранее."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM group_users WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            if cursor.fetchone():
                return False 

            cursor.execute("INSERT INTO group_users (group_id, user_id) VALUES (%s, %s)", (group_id, user_id))
            self.connection.commit()
            return True

    def get_user_group(self, tg_id):
        """Получение группы пользователя по его tg_id."""
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("SELECT id FROM users WHERE tg_id = %s", (str(tg_id),))
                user_row = cursor.fetchone()
                if user_row:
                    user_id = user_row[0]
                    
                    cursor.execute("""
                        SELECT g.id, g.name 
                        FROM groups g
                        JOIN group_users gu ON g.id = gu.group_id 
                        WHERE gu.user_id = %s
                    """, (user_id,))
                    group = cursor.fetchone()
                    return group 
                else:
                    return None
        except Exception as e:
            logging.error(f"Ошибка при получении группы пользователя: {e}")
            return None
        
    def get_all_groups(self):
        """Получение всех групп из базы данных."""
        groups = []
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("SELECT id, name FROM groups") 
                rows = cursor.fetchall()
                groups.extend(rows) 
        except Exception as e:
            logging.error(f"Ошибка при загрузке групп: {e}")
        return groups

    def is_user_in_group(self, group_id, user_id): #TODO use?
        """Проверка, находится ли пользователь в группе."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM group_users WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            return cursor.fetchone() is not None

    def get_allowed_chat_ids(self): # TODO 
        """Получение разрешенных chat_id из базы данных."""
        chat_ids = set()
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("SELECT chat_id FROM allowed_chats")  
                rows = cursor.fetchall()
                chat_ids.update(row[0] for row in rows) 
        except Exception as e:
            logging.error(f"Ошибка при получении разрешенных chat_id: {e}")
        return chat_ids

    def close(self):
        """Закрытие подключения к базе данных."""
        if self.connection:
            self.connection.close()
            logging.info("Подключение к базе данных закрыто.")
