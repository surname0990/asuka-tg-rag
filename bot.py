import os
import json
import numpy as np
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from sentence_transformers import SentenceTransformer
import faiss
import openai
from datetime import datetime
from database import Database  # Импортируем класс Database

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

class KnowledgeBot:
    def __init__(self, config):
        self.openai_api_key = config['openai_api_key']
        self.telegram_token = config['telegram_bot_token']
        self.database = Database(config['database_url'])  # Инициализация базы данных
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)
        self.documents = self.database.load_knowledge_base()  # Загружаем документы из БД

    def add_document(self, tg_id, chat_id, text):
        """Добавление документа в базу знаний и в базу данных."""
        timestamp = datetime.now()  # Получаем текущее время
        vector = self.model.encode(text)
        self.index.add(np.array([vector]).astype(np.float32))  
        self.documents.append(text)
        self.database.save_document(tg_id, chat_id, timestamp, text)  # Сохраняем документ в БД
        logger.info(f"Добавлен документ: {text}")

    def generate_response(self, closest_docs, query_text):
        """Генерация ответа на основе похожих документов."""
        prompt = f"Выводы на основе следующих документов: {closest_docs}\n\nЗапрос: {query_text}\n\nОтвет:"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Или gpt-4, если у вас есть доступ
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response['choices'][0]['message']['content']
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start."""
        await update.message.reply_text('Привет! Отправь мне текст, и я добавлю его в базу знаний.')

    async def add_document_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений для добавления документа."""
        tg_id = update.effective_user.id  # Получаем ID Telegram пользователя
        chat_id = update.effective_chat.id  # Получаем ID чата
        text = update.message.text
        self.add_document(tg_id, chat_id, text)
        
        await update.message.reply_text('Документ добавлен!')

    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик запросов на основе текста."""
        query_text = update.message.text
        query_vector = self.model.encode(query_text)

        k = 5  # количество ближайших документов
        distances, indices = self.index.search(np.array([query_vector]).astype(np.float32), k)

        logger.info(f"Запрос: {query_text}")
        logger.info(f"Найденные индексы: {indices[0]}, расстояния: {distances[0]}")

        valid_indices = [i for i in indices[0] if i >= 0]

        if valid_indices:
            closest_docs = [self.documents[i] for i in valid_indices]
            logger.info(f"Ближайшие документы: {closest_docs}")
            response = self.generate_response(closest_docs, query_text)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Не найдено похожих документов.")

    def run(self):
        """Запуск бота."""
        application = ApplicationBuilder().token(self.telegram_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_document_handler))  
        application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, self.query_handler))

        logger.info("Бот запущен.")
        application.run_polling()


def load_config(file_path='config.json'):
    """Загрузка конфигурации из JSON файла."""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)

if __name__ == '__main__':
    config = load_config()
    bot = KnowledgeBot(config)
    bot.run()
