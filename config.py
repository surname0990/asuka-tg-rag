import json
import os

def load_config(file_path='config.json'):
    """Загрузка конфигурации из JSON файла."""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)
