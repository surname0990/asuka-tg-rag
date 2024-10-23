import pinecone
import faiss

import numpy as np
import logging

# https://docs.pinecone.io/integrations/overview
class PineconeIndex:
    def __init__(self, api_key, environment):
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index("your-index-name") 

    def add_document(self, vector):
        """Добавление вектора документа в Pinecone."""
        vector_id = str(len(self.index.fetch()))  
        self.index.upsert([(vector_id, vector.tolist())])  
        logging.info(f"Вектор добавлен в Pinecone с ID {vector_id}.")

    def search(self, query_vector, k=5):
        """Поиск ближайших соседей."""
        query_response = self.index.query(query_vector.tolist(), top_k=k)
        return [match['id'] for match in query_response['matches']]  
    
class FAISSIndex:
    def __init__(self):
        self.index = faiss.IndexFlatL2(384) 
        self.documents = []

    def add_document(self, vector):
        """Добавление вектора документа в FAISS."""
        self.index.add(np.array([vector]).astype(np.float32))  
        logging.info("Вектор добавлен в FAISS.")

    def search(self, query_vector, k=5):
        """Поиск ближайших соседей."""
        distances, indices = self.index.search(np.array([query_vector]).astype(np.float32), k)
        if indices.size > 0:
            return [self.documents[i] for i in indices[0]]
        return []
