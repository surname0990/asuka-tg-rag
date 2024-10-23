import os
import openai
import faiss
import numpy as np
from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer

# Инициализация FastAPI
app = FastAPI()

# Инициализация OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Инициализация модели эмбеддингов
model = SentenceTransformer('all-MiniLM-L6-v2')

# Загружаем документацию
with open('documentation.txt', 'r', encoding='utf-8') as f:
    documents = f.readlines()

# Генерируем эмбеддинги для документации
doc_embeddings = model.encode(documents, convert_to_tensor=False)

# Инициализация FAISS индекса
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings))

# Функция для поиска по документам
def search_documents(query, top_k=5):
    query_embedding = model.encode([query], convert_to_tensor=False)
    distances, indices = index.search(np.array(query_embedding), top_k)
    results = [documents[idx] for idx in indices[0]]
    return results

# Маршрут для обработки запросов
@app.post("/ask")
async def ask_question(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    
    # Поиск по документации
    relevant_docs = search_documents(question, top_k=5)
    context = "\n".join(relevant_docs)
    
    # Формирование запроса к OpenAI
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Context: {context}\n\nQuestion: {question}\nAnswer:",
        max_tokens=1000,
        temperature=0.2,
    )
    
    answer = response.choices[0].text.strip()
    return {"answer": answer}
