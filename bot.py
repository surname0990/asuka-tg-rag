import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from sentence_transformers import SentenceTransformer
import openai
from datetime import datetime
from database import Database  
from index import FAISSIndexManager, PineconeIndexManager  

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

class KnowledgeBot:
    def __init__(self, config):
        openai.api_key = config['openai_api_key']
        self.telegram_token = config['telegram_bot_token']
        self.db = Database(config['database_url']) 
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

        # Выбор индекса (FAISS или Pinecone)
        if config['use_pinecone']:
            self.index_manager = PineconeIndexManager(config['pinecone_api_key'], config['pinecone_environment'])
        else:
            self.index_manager = FAISSIndexManager()
               
        self._initialize_group_indices()

    def _initialize_group_indices(self):
        """Инициализация индексов для всех групп."""
        groups = self.db.get_all_groups() 

        for group in groups:
            group_id = group[0]
            self._load_vectors(group_id) 

    def _load_vectors(self, group_id):
        """Загрузка векторов документов в индекс для конкретной группы."""
        documents = self.db.load_knowledge_base(group_id) 
        for doc in documents:
            vector = self.model.encode(doc)
            self.index_manager.add_document(group_id, vector, doc) 

    def add_document(self, tg_id, chat_id, text, group_id):
        """Добавление документа в базу знаний и в базу данных."""
        timestamp = datetime.now() 
        vector = self.model.encode(text)

        self.index_manager.add_document(group_id, vector, text)  
        self.db.save_document(tg_id, chat_id, timestamp, text, group_id)  

        logger.info(f"Добавлен документ: {text}")

    def generate_response(self, closest_docs, query_text):
        """Генерация ответа на основе похожих документов."""
        prompt = f"Выводы на основе следующих документов: {closest_docs}\n\nЗапрос: {query_text}\n\nОтвет:"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response['choices'][0]['message']['content']
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start."""
        user_id = update.effective_user.id 

        #Hardcode
        group_id = 1  # ID группы аналитиков
        added = self.db.add_user(group_id, user_id)

        if added:
            await update.message.reply_text(
                'Привет! Ты добавлен в группу аналитиков. '
                'Для каждой группы людей у меня своя нейронная сеть. '
                'Чтобы вносить документы в базу знаний, обратись к @dep_ton за доступом. '
                'В этом чате я также могу отвечать на ваши вопросы.'
            )
        else:
            await update.message.reply_text(
                'Привет! Ты уже в группе аналитиков. '
                'Чтобы вносить документы в базу знаний, обратись к @dep_ton за доступом. '
                'В этом чате я также могу отвечать на ваши вопросы.'
            )

    async def document_or_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        tg_id = update.effective_user.id 
        chat_id = update.effective_chat.id 
        text = update.message.text

        user_group = self.db.get_user_group(tg_id)

        if not user_group:
            await update.message.reply_text('Нажмите /start')
            return

        group_id, chat_type = self.db.get_group_by_chat_id(chat_id)
        
        if chat_type == 'document':
            self.add_document(tg_id, chat_id, text, group_id)
            await update.message.reply_text('Документ добавлен в базу знаний для вашей группы!')
        else:
            if group_id is None:
                group_id = user_group

            query_vector = self.model.encode(text)
            closest_docs = self.index_manager.search(group_id, query_vector)

            if closest_docs and len(closest_docs) > 0:
                response = self.generate_response(closest_docs, text)
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Не найдено похожих документов.")

    def run(self):
        """Запуск бота."""
        application = ApplicationBuilder().token(self.telegram_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.document_or_query_handler))  

        logger.info("Бот запущен.")
        application.run_polling()