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

    def add_document(self, group_id, vector, document):
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
        self.group_documents = {} 
    
    def get_or_create_index(self, group_id):
        """Получить или создать FAISS индекс для группы."""
        if group_id not in self.group_indices:
            self.group_indices[group_id] = faiss.IndexFlatL2(384)
            self.group_documents[group_id] = [] 
            logging.info(f"Создан новый FAISS индекс для группы {group_id}.")
        return self.group_indices[group_id]

    def add_document(self, group_id, vector, document):
        """Добавление вектора и документа в FAISS для определенной группы."""
        index = self.get_or_create_index(group_id)
        vector = np.array(vector).astype(np.float32).reshape(1, -1)
        index.add(vector)
        self.group_documents[group_id].append(document)
        logging.info(f"Вектор и документ добавлены в FAISS для группы {group_id}.")

    def search(self, group_id, query_vector, k=5):
        """Поиск ближайших соседей в FAISS для определенной группы."""
        group_id = group_id[0] if isinstance(group_id, tuple) else group_id

        if group_id not in self.group_indices:
            logging.error(f"Индекс для группы {group_id} не существует.")
            return []

        index = self.group_indices[group_id]
        query_vector = np.array(query_vector).astype(np.float32).reshape(1, -1)

        distances, indices = index.search(query_vector, k)
        
        results = []
        for i in indices[0]:
            if 0 <= i < len(self.group_documents[group_id]):
                results.append(self.group_documents[group_id][i])

        # if results:
        #     logging.info(f"Найдено {len(results)} документов для группы {group_id}.")
        # else:
        #     logging.info(f"Нет найденных документов для группы {group_id}.")

        return results
