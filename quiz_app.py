import json
import psycopg2
import random

def connect_db():
    """Connect to PostgreSQL"""
    return psycopg2.connect(
        dbname="quiz_app",
        user="fabianth",
        password="300699",
        host="localhost",
        port="5432"
    )

def create_table():
    """Create the quiz_questions table if it doesn't exist."""
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id SERIAL PRIMARY KEY,
            topic VARCHAR(50) NOT NULL,
            module VARCHAR(50),
            submodule VARCHAR(50),
            difficulty_level INT CHECK (difficulty_level BETWEEN 1 AND 3),
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            wrong_answer_1 TEXT NOT NULL,
            wrong_answer_2 TEXT NOT NULL,
            wrong_answer_3 TEXT,
            wrong_answer_4 TEXT,
            wrong_answer_5 TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def main_menu():
    """main menu"""
    while True:
        print("\n--- Command Line Quiz ---")
        print("1. Take a Quiz")
        print("2. Add a New Question")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            take_quiz()
        elif choice == "2":
            add_question()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def load_quiz():
    """Load the quiz json"""
    with open("questions.json", "r") as file:
        return json.load(file)

def take_quiz():
    """quiz function for choosing topics etc"""
    questions = load_quiz()
    topics = set(q["topic"] for q in questions)

    print("\nAviable Topics: ")
    for topic in topics:
        print(f"- {topic}")

    chosen_topic = input("\nEnter a Topic: ").strip().capitalize()

    filtered_questions = [q for q in questions if q["topic"] == chosen_topic]
    question = random.choice(filtered_questions)

    print(f"\nQuestion: {question['question']}")
    options = [question["correct_answer"]] + question["wrong_answers"]
    random.shuffle(options)

    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    answer = input("\nYour answer (enter the number): ").strip()
    
    if options[int(answer) - 1] == question["correct_answer"]:
        print("✅ Correct!\n")
    else:
        print(f"❌ Wrong! The correct answer is: {question['correct_answer']}\n")


def add_question():
    """Placeholder"""
    pass

if __name__ == "__main__":
        conn = connect_db()
        print("Connected to the database successfully!")
        conn.close()

        create_table()
        main_menu()
