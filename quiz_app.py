import psycopg2
import bcrypt
import random
import json
from psycopg2 import sql

def get_db_connection():
    return psycopg2.connect(
        dbname="quiz_app",
        user="fabianth",
        password="300699",
        host="localhost",
        port="5432"
    )

def check_password(password, hashed_password):
    if isinstance(hashed_password, memoryview):
        hashed_password = bytes(hashed_password)
    elif isinstance(hashed_password, str):
        if hashed_password.startswith('\\x'):
            hashed_password = bytes.fromhex(hashed_password[2:])
        else:
            hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def register_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("INSERT INTO users (username, password_hash) VALUES (%s, %s)"),
            [username, hashed_pw]
        )
        conn.commit()
        print("Registration successful!")
    except psycopg2.IntegrityError:
        print(f"Username {username} is already taken.")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Error during registration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def login_user(username, password):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("SELECT password_hash FROM users WHERE username = %s"),
            [username]
        )
        result = cursor.fetchone()
        
        if result:
            stored_hash = result[0]
            if check_password(password, stored_hash):
                print("Login successful!")
                return username
            else:
                print("Invalid password.")
        else:
            print("User not found.")
        return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_topics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT topic_id, topic_name FROM topics;")
    topics = cursor.fetchall()
    conn.close()
    return [{'topic_id': topic[0], 'name': topic[1]} for topic in topics]

def get_questions_by_topic(topic_id, limit=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, question, correct_answer, wrong_answer_1, wrong_answer_2, wrong_answer_3 FROM questions WHERE topic_id = %s"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query, (topic_id,))
    questions = cursor.fetchall()
    conn.close()
    return [{'question': question[1], 'correct_answer': question[2], 
             'wrong_answers': [question[3], question[4], question[5]]} for question in questions]

def add_new_question(current_user):
    if not current_user:
        print("Please login first.")
        return
        
    topics = get_all_topics()
    print("Available Topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic['name']}")
    try:
        topic_choice = int(input("Select a topic by number: "))
        if topic_choice < 1 or topic_choice > len(topics):
            print("Invalid selection.")
            return
        selected_topic = topics[topic_choice - 1]
    except ValueError:
        print("Invalid input.")
        return
        
    print(f"Adding a new question for {selected_topic['name']}.")
    module = input("Enter module: ")
    submodule = input("Enter submodule: ")
    difficulty_level = int(input("Enter difficulty level (1-3): "))
    question_text = input("Enter the question: ")
    correct_answer = input("Enter the correct answer: ")
    wrong_answers = [input(f"Enter wrong answer {i + 1}: ") for i in range(3)]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO questions (topic_id, module, submodule, difficulty_level, question, correct_answer, "
        "wrong_answer_1, wrong_answer_2, wrong_answer_3) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
        (selected_topic['topic_id'], module, submodule, difficulty_level, question_text, correct_answer,
         wrong_answers[0], wrong_answers[1], wrong_answers[2])
    )
    conn.commit()
    conn.close()
    print(f"Question added successfully to {selected_topic['name']}.")

def start_quiz(current_user):
    if not current_user:
        print("Please login first.")
        return
        
    topics = get_all_topics()
    print("Available Topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic['name']}")
    try:
        topic_choice = int(input("Select a topic by number: "))
        if topic_choice < 1 or topic_choice > len(topics):
            print("Invalid selection.")
            return
        selected_topic = topics[topic_choice - 1]
    except ValueError:
        print("Invalid input.")
        return
        
    # Get total questions available
    total_questions = len(get_questions_by_topic(selected_topic['topic_id']))
    if total_questions == 0:
        print(f"No questions available for {selected_topic['name']}.")
        return
        
    # Ask how many questions to include
    while True:
        try:
            num_questions = int(input(f"How many questions would you like? (1-{total_questions}): "))
            if 1 <= num_questions <= total_questions:
                break
            else:
                print(f"Please enter a number between 1 and {total_questions}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    questions = get_questions_by_topic(selected_topic['topic_id'], num_questions)
    random.shuffle(questions)  # Shuffle the questions
    
    score = 0
    print(f"\nStarting quiz on {selected_topic['name']}!")
    print(f"Total questions: {len(questions)}\n")
    
    for idx, question in enumerate(questions, start=1):
        print(f"Question {idx}: {question['question']}")
        answers = question['wrong_answers'] + [question['correct_answer']]
        random.shuffle(answers)
        
        for i, ans in enumerate(answers, start=1):
            print(f"{i}. {ans}")
            
        try:
            user_answer = int(input("Your answer (1-4): "))
            if 1 <= user_answer <= 4:
                if answers[user_answer - 1] == question["correct_answer"]:
                    print("✅ Correct!")
                    score += 1
                else:
                    print(f"❌ Wrong! The correct answer was: {question['correct_answer']}")
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        
        print()

    print(f"\nQuiz completed! Your final score: {score}/{len(questions)}")
    print("Thanks for playing!")

def view_existing_questions(current_user):
    if not current_user:
        print("Please login first.")
        return
        
    topics = get_all_topics()
    print("Available Topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic['name']}")
    try:
        topic_choice = int(input("Select a topic by number: "))
        if topic_choice < 1 or topic_choice > len(topics):
            print("Invalid selection.")
            return
        selected_topic = topics[topic_choice - 1]
    except ValueError:
        print("Invalid input.")
        return
        
    questions = get_questions_by_topic(selected_topic['topic_id'])
    if not questions:
        print(f"No questions available for {selected_topic['name']}.")
        return
        
    print(f"\nQuestions for {selected_topic['name']}:")
    for idx, question in enumerate(questions, start=1):
        print(f"\nQ{idx}: {question['question']}")
        print(f"Correct Answer: {question['correct_answer']}")
        print("Wrong Answers:")
        for i, ans in enumerate(question['wrong_answers'], start=1):
            print(f"{i}. {ans}")

def load_data_from_json(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'.")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    topics = {}
    for entry in data:
        topic_name = entry['topic']
        cursor.execute("SELECT topic_id FROM topics WHERE topic_name = %s;", (topic_name,))
        existing_topic = cursor.fetchone()
        
        if not existing_topic:
            cursor.execute("INSERT INTO topics (topic_name) VALUES (%s) RETURNING topic_id;", (topic_name,))
            topic_id = cursor.fetchone()[0]
            topics[topic_name] = topic_id
        else:
            topics[topic_name] = existing_topic[0]
    
    for entry in data:
        topic_id = topics[entry['topic']]
        cursor.execute(
            "INSERT INTO questions (topic_id, module, submodule, difficulty_level, question, correct_answer, "
            "wrong_answer_1, wrong_answer_2, wrong_answer_3) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (topic_id, entry['module'], entry['submodule'], entry['difficulty_level'],
             entry['question'], entry['correct_answer'],
             entry['wrong_answers'][0], entry['wrong_answers'][1], entry['wrong_answers'][2])
        )
    
    conn.commit()
    conn.close()
    print("Data loaded successfully from JSON!")

def main():
    current_user = None
    while True:
        print("\nMain Menu:")
        print("1. Register")
        print("2. Login")
        print("3. Start Quiz")
        print("4. Add New Question")
        print("5. View Existing Questions")
        print("6. Load data from JSON")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if username and password:
                register_user(username, password)
            else:
                print("Username and password cannot be empty.")
                
        elif choice == "2":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if username and password:
                current_user = login_user(username, password)
            else:
                print("Username and password cannot be empty.")
                
        elif choice == "3":
            if current_user:
                start_quiz(current_user)
            else:
                print("Please login first.")
                
        elif choice == "4":
            if current_user:
                add_new_question(current_user)
            else:
                print("Please login first.")
                
        elif choice == "5":
            if current_user:
                view_existing_questions(current_user)
            else:
                print("Please login first.")
                
        elif choice == "6":
            json_file = input("Enter JSON filename (default: questions.json): ").strip() or "questions.json"
            load_data_from_json(json_file)
            
        elif choice == "7":
            print("Exiting the quiz application. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()