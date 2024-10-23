import logging
from bot import KnowledgeBot
from config import load_config

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    config = load_config()
    bot = KnowledgeBot(config)
    bot.run()