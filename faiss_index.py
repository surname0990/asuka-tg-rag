import faiss
import numpy as np
import logging

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
