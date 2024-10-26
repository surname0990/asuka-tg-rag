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
                    ON CONFLICT (tg_id, chat_id) DO NOTHING
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

    def add_user(self, group_id, tg_id):
        """Добавление пользователя в таблицу users и связывание с группой в group_users."""
        try:
            with closing(self.connection.cursor()) as cursor:
                tg_id_str = str(tg_id)
                group_id_str = str(group_id)

                cursor.execute("""
                    INSERT INTO users (tg_id, role, group_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (tg_id) DO NOTHING
                    RETURNING id
                """, (tg_id_str, 'user', group_id_str))
                    
                user_id = cursor.fetchone()
                if user_id is not None:
                    user_id = user_id[0]
                    
                    cursor.execute("""
                        INSERT INTO group_users (group_id, user_id)
                        VALUES (%s, %s)
                        ON CONFLICT (group_id, user_id) DO NOTHING
                    """, (group_id_str, user_id))
                    
                    self.connection.commit() 
                    return user_id  
                else:
                    logging.info("Пользователь уже существует.")
                    return None

        except Exception as e:
            logging.error(f"Ошибка при добавлении пользователя: {e}")
            self.connection.rollback()
            return None

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
                    logging.info("Пользователь не найден.")
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

    def get_group_by_chat_id(self, chat_id):
        """Получение группы по chat_id."""
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute("""
                    SELECT g.id, gc.chat_type 
                    FROM groups g
                    JOIN group_chats gc ON g.id = gc.group_id 
                    WHERE gc.chat_id = %s
                """, (str(chat_id),)) 
                result = cursor.fetchone()  
                return result if result else (None, None) 
        except Exception as e:
            logging.error(f"Ошибка при получении группы по chat_id: {e}")
            return None, None
        
    def close(self):
        """Закрытие подключения к базе данных."""
        if self.connection:
            self.connection.close()
            logging.info("Подключение к базе данных закрыто.")
