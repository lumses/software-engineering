CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name VARCHAR(100),
    surname VARCHAR(100),
    email VARCHAR(100),
    age INTEGER
);

CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS user_index ON users(login, surname, name);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);

INSERT INTO users (login, password, name, surname, email, age) VALUES
('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'John', 'Doe', 'admin@example.com', 30),
('jdoe', '$2b$12$abc1234567890examplehashhere', 'Jane', 'Doe', 'jane.doe@example.com', 28),
('bsmith', '$2b$12$abc1234567890examplehashhere', 'Bob', 'Smith', 'bob.smith@example.com', 35),
('ajohnson', '$2b$12$abc1234567890examplehashhere', 'Alice', 'Johnson', 'alice.j@example.com', 24),
('mwhite', '$2b$12$abc1234567890examplehashhere', 'Michael', 'White', 'mwhite@example.com', 40)
ON CONFLICT DO NOTHING;

INSERT INTO posts (id, user_id, content) VALUES
(gen_random_uuid(), 1, 'Hello, world!'),
(gen_random_uuid(), 3, 'Test message'),
(gen_random_uuid(), 3, 'Another post'),
(gen_random_uuid(), 4, 'Bye, world!');