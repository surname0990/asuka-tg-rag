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
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

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

        self.index_manager.add_document(group_id, vector)  
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
        await update.message.reply_text('Привет! Отправь мне текст, и я добавлю его в базу знаний.')

    async def add_document_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений для добавления документа."""
        tg_id = update.effective_user.id 
        chat_id = update.effective_chat.id 
        text = update.message.text

        allowed_chat_ids = self.db.get_allowed_chat_ids()
        
        if chat_id not in allowed_chat_ids:
            await update.message.reply_text('Добавление документов разрешено только в определенных чатах.')
            return

        group = self.db.get_user_group(tg_id)
        
        if group:
            group_id = group[0]  
            self.add_document(tg_id, chat_id, text, group_id)
            await update.message.reply_text('Документ добавлен в вашу группу!')
        else:
            await update.message.reply_text('Вы не принадлежите ни одной касте.')

    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик запросов на основе текста."""
        # query_text = update.message.text
        query_text = update.message.text.replace('/query', '').strip()
        query_vector = self.model.encode(query_text)
        tg_id = update.effective_user.id

        group = self.db.get_user_group(tg_id)
        if group:
            group_id = group[0] 
            closest_docs = self.index_manager.search(group_id, query_vector)
            
            if closest_docs is not None and len(closest_docs) > 0:
                response = self.generate_response(closest_docs, query_text)
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Не найдено похожих документов.")
        else:
            await update.message.reply_text('Вы не принадлежите ни одной касте.')

    async def add_user_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Добавление пользователя в группу. Только для администраторов."""
        user_id = update.effective_user.id
        group_id = 1  #TODO

        chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_id) 

        if chat_member.status not in ['administrator', 'creator']: # TODO
            await update.message.reply_text('У вас нет прав для добавления пользователей в группу.')
            return

        target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        if not target_user:
            await update.message.reply_text("Пожалуйста, укажите пользователя, которого хотите добавить.")
            return

        username = f"@{target_user.username}" if target_user.username else f"{target_user.first_name} {target_user.last_name or ''}".strip()

        added = self.db.add_user_to_group(group_id, target_user.id)

        if added:
            await update.message.reply_text(f'Пользователь {username} успешно добавлен в группу.')
        else:
            await update.message.reply_text(f'Пользователь {username} уже в группе.')

    def run(self):
        """Запуск бота."""
        application = ApplicationBuilder().token(self.telegram_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_document_handler))  
        application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, self.query_handler))
        application.add_handler(CommandHandler("adduser", self.add_user_to_group)) 

        logger.info("Бот запущен.")
        application.run_polling()