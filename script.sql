DROP DATABASE IF EXISTS quiz_app;
CREATE DATABASE quiz_app;
\c quiz_app;

CREATE TABLE public.topics (
    topic_id SERIAL PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE public.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.math_questions (
    id SERIAL PRIMARY KEY,
    module TEXT,
    submodule TEXT,
    difficulty_level INTEGER,
    question TEXT,
    correct_answer TEXT,
    wrong_answers TEXT[]
);

CREATE TABLE public.questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER,
    module VARCHAR(255) NOT NULL,
    submodule VARCHAR(255) NOT NULL,
    difficulty_level INTEGER CHECK (difficulty_level >= 1 AND difficulty_level <= 3),
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    wrong_answer_1 TEXT NOT NULL,
    wrong_answer_2 TEXT NOT NULL,
    wrong_answer_3 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT questions_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(topic_id) ON DELETE CASCADE
);

CREATE TABLE public.quiz_results (
    result_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    topic_id INTEGER,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT quiz_results_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id),
    CONSTRAINT quiz_results_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(topic_id)
);
