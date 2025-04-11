import psycopg2
import random
import json

def get_db_connection():
    return psycopg2.connect(
        dbname="quiz_app",
        user="fabianth",
        password="300699",
        host="localhost",
        port="5432"
    )

def get_all_topics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT topic_id, topic_name FROM topics;")
    topics = cursor.fetchall()
    conn.close()
    return [{'topic_id': topic[0], 'name': topic[1]} for topic in topics]

def get_questions_by_topic(topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, correct_answer, wrong_answer_1, wrong_answer_2, wrong_answer_3 "
        "FROM questions WHERE topic_id = %s;", (topic_id,)
    )
    questions = cursor.fetchall()
    conn.close()
    return [{'question': question[1], 'correct_answer': question[2], 
             'wrong_answers': [question[3], question[4], question[5]]} for question in questions]

def add_new_question():
    topics = get_all_topics()

    print("Available Topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic['name']}")

    try:
        topic_choice = int(input("Select a topic by number: "))
        if topic_choice < 1 or topic_choice > len(topics):
            print("Invalid selection. Please choose a valid topic number.")
            return
        selected_topic = topics[topic_choice - 1]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    print(f"Adding a new question for {selected_topic['name']}.")

    module = input("Enter module: ")
    submodule = input("Enter submodule: ")
    difficulty_level = int(input("Enter difficulty level (1-3): "))
    question_text = input("Enter the question: ")
    correct_answer = input("Enter the correct answer: ")
    wrong_answers = []
    for i in range(3):
        wrong_answers.append(input(f"Enter wrong answer {i + 1}: "))

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

def start_quiz():
    topics = get_all_topics()

    print("Available Topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic['name']}")

    try:
        topic_choice = int(input("Select a topic by number: "))
        if topic_choice < 1 or topic_choice > len(topics):
            print("Invalid selection. Please choose a valid topic number.")
            return
        selected_topic = topics[topic_choice - 1]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    questions = get_questions_by_topic(selected_topic['topic_id'])
    
    if not questions:
        print(f"No questions available for {selected_topic['name']}.")
        return

    score = 0
    print(f"Starting quiz on {selected_topic['name']}!\n")
    for idx, question in enumerate(questions):
        print(f"Question {idx + 1}: {question['question']}")
        
        answers = question['wrong_answers'] + [question['correct_answer']]
        random.shuffle(answers)

        for i, ans in enumerate(answers, 1):
            print(f"{i}. {ans}")

        try:
            user_answer = int(input("Your answer (1-4): "))
            if answers[user_answer - 1] == question["correct_answer"]:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Wrong! The correct answer was: {question['correct_answer']}")
        except (ValueError, IndexError):
            print("Invalid input, please choose a number between 1 and 4.")
        
        print()

    print(f"Your final score: {score}/{len(questions)}")
    print("Thanks for playing!")

def view_existing_questions():
    topics = get_all_topics()

    print("Available Topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic['name']}")

    try:
        topic_choice = int(input("Select a topic by number: "))
        if topic_choice < 1 or topic_choice > len(topics):
            print("Invalid selection. Please choose a valid topic number.")
            return
        selected_topic = topics[topic_choice - 1]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    questions = get_questions_by_topic(selected_topic['topic_id'])
    
    if not questions:
        print(f"No questions available for {selected_topic['name']}.")
        return

    print(f"Questions for {selected_topic['name']}:\n")
    for idx, question in enumerate(questions):
        print(f"Q{idx + 1}: {question['question']}")
        print(f"Correct Answer: {question['correct_answer']}")
        print(f"Wrong Answers: {', '.join(question['wrong_answers'])}\n")

def load_data_from_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

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
    print("Topics and questions loaded successfully!")

def main():
    while True:
        print("1. Start Quiz")
        print("2. Add New Question")
        print("3. View Existing Questions")
        print("4. Exit")
        print("5. Load data from JSON")
        choice = input("Enter your choice: ")

        if choice == "1":
            start_quiz()
        elif choice == "2":
            add_new_question()
        elif choice == "3":
            view_existing_questions()
        elif choice == "4":
            print("Exiting...")
            break
        elif choice == "5":
            load_data_from_json('questions.json')
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()