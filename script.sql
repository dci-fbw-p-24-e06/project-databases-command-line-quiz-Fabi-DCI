CREATE TABLE IF NOT EXISTS topics (
    topic_id SERIAL PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    question_id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(topic_id),
    module VARCHAR(255),
    submodule VARCHAR(255),
    difficulty_level INTEGER,
    question TEXT,
    correct_answer TEXT,
    wrong_answers TEXT[]
);
