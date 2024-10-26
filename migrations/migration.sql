CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    group_id BIGINT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS group_users (
    group_id BIGINT NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    tg_id VARCHAR(255) NOT NULL,
    chat_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    text TEXT NOT NULL,
    group_id BIGINT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    CONSTRAINT unique_tg_chat UNIQUE (tg_id, chat_id)
);

CREATE TABLE IF NOT EXISTS group_chats (
    chat_id VARCHAR(255) PRIMARY KEY,
    group_id BIGINT NOT NULL,
    chat_type VARCHAR(50) NOT NULL DEFAULT 'document',
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

INSERT INTO groups (name) VALUES
    ('Группа 1'),
    ('Группа 2'),
    ('Группа 3')
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (tg_id, role, group_id) VALUES
    ('6780382827', 'admin', 1)
ON CONFLICT (tg_id) DO NOTHING;

INSERT INTO group_users (group_id, user_id) VALUES
    (1, 1)
ON CONFLICT (group_id, user_id) DO NOTHING;

INSERT INTO documents (tg_id, chat_id, timestamp, text, group_id) VALUES
    ('6780382827', '6780382827', '2024-10-25 20:39:21.943861','Что такое Azuka? Azuka — это Telegram-бот, который помогает пользователям добавлять документы и задавать вопросы. Используя нейросетевые технологии, он предоставляет быстрые и точные ответы, а также организует информацию по группам пользователей. Основные функции: Добавление документов: Пользователи могут отправлять документы, которые будут сохранены в базе данных. Задавание вопросов: Бот позволяет пользователям задавать вопросы и получать ответы на основе хранящихся документов. Управление группами: Поддержка нескольких групп пользователей, каждая из которых имеет доступ к своей базе знаний. Структура базы данных: Azuka использует PostgreSQL для хранения информации. Вот основные таблицы, с которыми вы будете работать: groups: Хранит информацию о группах пользователей, таких как названия и уникальные идентификаторы. users: Содержит данные о пользователях, их ролях и принадлежности к группам. documents: Сохраняет отправленные документы и их метаданные (временные метки, текст и идентификаторы групп). group_chats: Связывает чаты с группами, определяя их тип и уникальные идентификаторы. Приватность и безопасность: Azuka разработан с акцентом на безопасность данных: Защита данных: Все пользовательские данные и документы хранятся в защищенной базе данных PostgreSQL. Авторизация: Бот требует авторизации пользователей, чтобы гарантировать доступ только для участников групп. Конфиденциальность: Бот не делится личными данными пользователей с третьими сторонами. Как использовать Azuka? Для того чтобы начать взаимодействие с Azuka, следуйте этим простым шагам: Запуск бота: Отправьте команду /start в чате с ботом. Это позволит вам начать взаимодействие и добавит вас в систему. Добавление документа: Отправьте текст или документ в чат. Бот подтвердит успешное добавление. Задавание вопросов: Направьте ваш вопрос в чат. Бот обработает запрос и предоставит ответ на основе сохраненных документов. Работа с группами: Если вы состоите в нескольких группах, бот будет адаптировать свои ответы в зависимости от контекста группы. Применение Azuka: Azuka может быть использован в различных сферах: Корпоративные знания: Упрощает доступ к корпоративной документации и внутренним процессам. Образовательные учреждения: Помогает студентам и преподавателям находить и делиться учебными материалами. Поддержка клиентов: Автоматизирует процесс ответов на часто задаваемые вопросы, улучшая взаимодействие с клиентами. Заключение: Azuka — это удобный и мощный инструмент для управления знаниями и документооборотом. Он позволяет пользователям быстро находить и делиться информацией, обеспечивая при этом безопасность и конфиденциальность данных. Начните использовать Azuka уже сегодня и упростите управление своими знаниями!', 1)
ON CONFLICT (tg_id, chat_id) DO NOTHING;

INSERT INTO group_chats (chat_id, group_id, chat_type) VALUES
    ('6780382827', 1, 'document')
ON CONFLICT (chat_id) DO NOTHING;

INSERT INTO group_chats (chat_id, group_id, chat_type) VALUES
    ('6780382828', 1, 'query')
ON CONFLICT (chat_id) DO NOTHING;
