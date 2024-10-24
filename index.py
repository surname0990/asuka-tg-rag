import pinecone
import faiss

import numpy as np
import logging

class PineconeIndexManager:
    def __init__(self, api_key, environment):
        pinecone.init(api_key=api_key, environment=environment)
        self.group_indices = {} 
    
    def get_or_create_index(self, group_id):
        """Получить или создать Pinecone индекс для группы."""
        if group_id not in self.group_indices:
            index_name = f"group_{group_id}_index"
            if not pinecone.list_indexes():
                pinecone.create_index(index_name, dimension=384) 
            self.group_indices[group_id] = pinecone.Index(index_name)
            logging.info(f"Создан новый Pinecone индекс для группы {group_id}.")
        return self.group_indices[group_id]

    def add_document(self, group_id, vector):
        """Добавление вектора документа в Pinecone для определенной группы."""
        index = self.get_or_create_index(group_id)
        vector_id = str(len(index.fetch())) 
        index.upsert([(vector_id, vector.tolist())])  
        logging.info(f"Вектор добавлен в Pinecone для группы {group_id} с ID {vector_id}.")

    def search(self, group_id, query_vector, k=5):
        """Поиск ближайших соседей в Pinecone для определенной группы."""
        index = self.get_or_create_index(group_id)
        query_response = index.query(query_vector.tolist(), top_k=k)
        return [match['id'] for match in query_response['matches']]  


class FAISSIndexManager:
    def __init__(self):
        self.group_indices = {} 
    
    def get_or_create_index(self, group_id):
        """Получить или создать FAISS индекс для группы."""
        if group_id not in self.group_indices:
            self.group_indices[group_id] = faiss.IndexFlatL2(384)
            logging.info(f"Создан новый FAISS индекс для группы {group_id}.")
        return self.group_indices[group_id]

    def add_document(self, group_id, vector):
        """Добавление вектора документа в FAISS для определенной группы."""
        index = self.get_or_create_index(group_id)
        index.add(np.array([vector]).astype(np.float32))  
        logging.info(f"Вектор добавлен в FAISS для группы {group_id}.")

    def search(self, group_id, query_vector, k=5):
        """Поиск ближайших соседей в FAISS для определенной группы."""
        index = self.get_or_create_index(group_id)
        distances, indices = index.search(np.array([query_vector]).astype(np.float32), k)
        if indices.size > 0:
            return indices[0]
        return []
