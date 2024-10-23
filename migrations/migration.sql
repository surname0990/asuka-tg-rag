CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,         
    tg_id VARCHAR(255) UNIQUE NOT NULL, 
    position VARCHAR(255) NOT NULL, -- Должность
    project VARCHAR(255) NOT NULL,  -- Проект
);

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,          
    name VARCHAR(255) UNIQUE NOT NULL 
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    text TEXT NOT NULL
);
