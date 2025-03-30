import psycopg2

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

def take_quiz():
    """Placeholder"""
    pass

def add_question():
    """Placeholder"""
    pass

if __name__ == "__main__":
        conn = connect_db()
        print("Connected to the database successfully!")
        conn.close()

        create_table()
        main_menu()
