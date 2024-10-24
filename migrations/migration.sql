CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    group_id INTEGER NOT NULL 
);

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS group_users (
    group_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    text TEXT NOT NULL,
    group_id INTEGER NOT NULL 
);

CREATE TABLE allowed_chats (
    chat_id BIGINT PRIMARY KEY
);