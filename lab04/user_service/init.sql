CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name VARCHAR(100),
    surname VARCHAR(100),
    email VARCHAR(100),
    age INTEGER
);

CREATE INDEX IF NOT EXISTS user_index ON users(login, surname, name);

INSERT INTO users (login, password, name, surname, email, age) VALUES
('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'John', 'Doe', 'admin@example.com', 30),
('jdoe', '$2b$12$abc1234567890examplehashhere', 'Jane', 'Doe', 'jane.doe@example.com', 28),
('bsmith', '$2b$12$abc1234567890examplehashhere', 'Bob', 'Smith', 'bob.smith@example.com', 35),
('ajohnson', '$2b$12$abc1234567890examplehashhere', 'Alice', 'Johnson', 'alice.j@example.com', 24),
('mwhite', '$2b$12$abc1234567890examplehashhere', 'Michael', 'White', 'mwhite@example.com', 40)
ON CONFLICT DO NOTHING;
