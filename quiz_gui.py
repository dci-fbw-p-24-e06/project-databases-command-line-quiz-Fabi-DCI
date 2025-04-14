import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QStackedWidget, QListWidget,
                            QMessageBox, QRadioButton, QButtonGroup, QGroupBox, QTextEdit,
                            QSpinBox, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import quiz_app

class LoginRegisterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Quiz Application")
        title.setFont(QFont('Arial', 24))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Image/Logo
        logo_label = QLabel()
        pixmap = QPixmap("quiz_icon.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)
        
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)
        buttons_layout.addWidget(self.register_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty.")
            return
            
        current_user = quiz_app.login_user(username, password)
        if current_user:
            self.parent.current_user = current_user
            self.parent.update_user_status()
            self.parent.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
    
    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty.")
            return
            
        quiz_app.register_user(username, password)
        self.username_input.clear()
        self.password_input.clear()

class MainMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Welcome message
        self.welcome_label = QLabel()
        self.welcome_label.setFont(QFont('Arial', 16))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_label)
        
        # Menu buttons
        self.start_quiz_button = QPushButton("Start Quiz")
        self.start_quiz_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(2))
        layout.addWidget(self.start_quiz_button)
        
        self.add_question_button = QPushButton("Add New Question")
        self.add_question_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(3))
        layout.addWidget(self.add_question_button)
        
        self.view_questions_button = QPushButton("View Existing Questions")
        self.view_questions_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(4))
        layout.addWidget(self.view_questions_button)
        
        self.load_json_button = QPushButton("Load Data from JSON")
        self.load_json_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(5))
        layout.addWidget(self.load_json_button)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        layout.addWidget(self.logout_button)
        
        self.setLayout(layout)
    
    def update_welcome_message(self):
        if self.parent.current_user:
            self.welcome_label.setText(f"Welcome, {self.parent.current_user}!")
        else:
            self.welcome_label.setText("Welcome!")
    
    def handle_logout(self):
        self.parent.current_user = None
        self.parent.update_user_status()
        self.parent.stacked_widget.setCurrentIndex(0)

class QuizSetupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Quiz Setup")
        title.setFont(QFont('Arial', 18))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Topic selection
        self.topic_combo = QComboBox()
        self.populate_topics()
        layout.addWidget(QLabel("Select Topic:"))
        layout.addWidget(self.topic_combo)
        
        # Number of questions
        layout.addWidget(QLabel("Number of Questions:"))
        self.question_count = QSpinBox()
        self.question_count.setMinimum(1)
        self.question_count.setMaximum(20)
        layout.addWidget(self.question_count)
        
        # Start button
        start_button = QPushButton("Start Quiz")
        start_button.clicked.connect(self.start_quiz)
        layout.addWidget(start_button)
        
        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_button)
        
        self.setLayout(layout)
    
    def populate_topics(self):
        self.topic_combo.clear()
        topics = quiz_app.get_all_topics()
        for topic in topics:
            self.topic_combo.addItem(topic['name'], topic['topic_id'])
        
        # Update question count when topic changes
        self.topic_combo.currentIndexChanged.connect(self.update_question_count)
        if self.topic_combo.count() > 0:
            self.update_question_count()
    
    def update_question_count(self):
        topic_id = self.topic_combo.currentData()
        if topic_id:
            questions = quiz_app.get_questions_by_topic(topic_id)
            self.question_count.setMaximum(len(questions))
    
    def start_quiz(self):
        if not self.parent.current_user:
            QMessageBox.warning(self, "Error", "Please login first.")
            return
            
        topic_id = self.topic_combo.currentData()
        num_questions = self.question_count.value()
        
        if topic_id and num_questions > 0:
            self.parent.quiz_widget.start_quiz(topic_id, num_questions)
            self.parent.stacked_widget.setCurrentIndex(6)

class AddQuestionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Add New Question")
        title.setFont(QFont('Arial', 18))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Topic selection
        self.topic_combo = QComboBox()
        self.populate_topics()
        layout.addWidget(QLabel("Select Topic:"))
        layout.addWidget(self.topic_combo)
        
        # Module
        layout.addWidget(QLabel("Module:"))
        self.module_input = QLineEdit()
        layout.addWidget(self.module_input)
        
        # Submodule
        layout.addWidget(QLabel("Submodule:"))
        self.submodule_input = QLineEdit()
        layout.addWidget(self.submodule_input)
        
        # Difficulty
        layout.addWidget(QLabel("Difficulty Level (1-3):"))
        self.difficulty_input = QSpinBox()
        self.difficulty_input.setMinimum(1)
        self.difficulty_input.setMaximum(3)
        layout.addWidget(self.difficulty_input)
        
        # Question
        layout.addWidget(QLabel("Question:"))
        self.question_input = QTextEdit()
        layout.addWidget(self.question_input)
        
        # Correct answer
        layout.addWidget(QLabel("Correct Answer:"))
        self.correct_answer_input = QLineEdit()
        layout.addWidget(self.correct_answer_input)
        
        # Wrong answers
        layout.addWidget(QLabel("Wrong Answers:"))
        self.wrong_answer1_input = QLineEdit()
        self.wrong_answer2_input = QLineEdit()
        self.wrong_answer3_input = QLineEdit()
        layout.addWidget(QLabel("Wrong Answer 1:"))
        layout.addWidget(self.wrong_answer1_input)
        layout.addWidget(QLabel("Wrong Answer 2:"))
        layout.addWidget(self.wrong_answer2_input)
        layout.addWidget(QLabel("Wrong Answer 3:"))
        layout.addWidget(self.wrong_answer3_input)
        
        # Submit button
        submit_button = QPushButton("Submit Question")
        submit_button.clicked.connect(self.submit_question)
        layout.addWidget(submit_button)
        
        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_button)
        
        self.setLayout(layout)
    
    def populate_topics(self):
        self.topic_combo.clear()
        topics = quiz_app.get_all_topics()
        for topic in topics:
            self.topic_combo.addItem(topic['name'], topic['topic_id'])
    
    def submit_question(self):
        if not self.parent.current_user:
            QMessageBox.warning(self, "Error", "Please login first.")
            return
            
        topic_id = self.topic_combo.currentData()
        module = self.module_input.text()
        submodule = self.submodule_input.text()
        difficulty = self.difficulty_input.value()
        question = self.question_input.toPlainText()
        correct_answer = self.correct_answer_input.text()
        wrong_answers = [
            self.wrong_answer1_input.text(),
            self.wrong_answer2_input.text(),
            self.wrong_answer3_input.text()
        ]
        
        if not all([topic_id, module, submodule, question, correct_answer] + wrong_answers):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
            
        try:
            quiz_app.add_new_question(self.parent.current_user)
            QMessageBox.information(self, "Success", "Question added successfully!")
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add question: {str(e)}")
    
    def clear_form(self):
        self.module_input.clear()
        self.submodule_input.clear()
        self.difficulty_input.setValue(1)
        self.question_input.clear()
        self.correct_answer_input.clear()
        self.wrong_answer1_input.clear()
        self.wrong_answer2_input.clear()
        self.wrong_answer3_input.clear()

class ViewQuestionsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("View Questions")
        title.setFont(QFont('Arial', 18))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Topic selection
        self.topic_combo = QComboBox()
        self.populate_topics()
        layout.addWidget(QLabel("Select Topic:"))
        layout.addWidget(self.topic_combo)
        
        # Questions list
        self.questions_list = QListWidget()
        layout.addWidget(self.questions_list)
        
        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_button)
        
        self.setLayout(layout)
        
        # Connect topic change to update questions
        self.topic_combo.currentIndexChanged.connect(self.update_questions_list)
    
    def populate_topics(self):
        self.topic_combo.clear()
        topics = quiz_app.get_all_topics()
        for topic in topics:
            self.topic_combo.addItem(topic['name'], topic['topic_id'])
    
    def update_questions_list(self):
        self.questions_list.clear()
        topic_id = self.topic_combo.currentData()
        if topic_id:
            questions = quiz_app.get_questions_by_topic(topic_id)
            for q in questions:
                self.questions_list.addItem(q['question'])

class LoadJsonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Load Data from JSON")
        title.setFont(QFont('Arial', 18))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("questions.json")
        file_layout.addWidget(self.file_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)
        
        # Load button
        load_button = QPushButton("Load Data")
        load_button.clicked.connect(self.load_data)
        layout.addWidget(load_button)
        
        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_button)
        
        self.setLayout(layout)
    
    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            self.file_input.setText(filename)
    
    def load_data(self):
        filename = self.file_input.text() or "questions.json"
        try:
            quiz_app.load_data_from_json(filename)
            QMessageBox.information(self, "Success", "Data loaded successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load data: {str(e)}")

class QuizWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_question = 0
        self.score = 0
        self.questions = []
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Question display
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Arial', 14))
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)
        
        # Answer options
        self.answer_group = QButtonGroup()
        self.answer_widgets = []
        
        for i in range(4):
            answer_widget = QRadioButton()
            answer_widget.setFont(QFont('Arial', 12))
            self.answer_group.addButton(answer_widget, i)
            self.answer_widgets.append(answer_widget)
            layout.addWidget(answer_widget)
        
        # Submit button
        self.submit_button = QPushButton("Submit Answer")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button)
        
        # Progress and score
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Back button (hidden during quiz)
        self.back_button = QPushButton("Back to Menu")
        self.back_button.clicked.connect(self.finish_quiz)
        layout.addWidget(self.back_button)
        self.back_button.hide()
        
        self.setLayout(layout)
    
    def start_quiz(self, topic_id, num_questions):
        self.current_question = 0
        self.score = 0
        all_questions = quiz_app.get_questions_by_topic(topic_id)
        self.questions = random.sample(all_questions, num_questions)
        self.show_question()
        self.back_button.hide()
        self.submit_button.show()
    
    def show_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.question_label.setText(question['question'])
            
            # Prepare answers
            answers = question['wrong_answers'] + [question['correct_answer']]
            random.shuffle(answers)
            
            # Update radio buttons
            for i in range(4):
                self.answer_widgets[i].setText(answers[i])
                self.answer_widgets[i].setChecked(False)
            
            # Update progress
            self.progress_label.setText(
                f"Question {self.current_question + 1} of {len(self.questions)} | "
                f"Score: {self.score}/{self.current_question}"
            )
        else:
            self.finish_quiz()
    
    def check_answer(self):
        if not self.answer_group.checkedButton():
            QMessageBox.warning(self, "Error", "Please select an answer.")
            return
            
        selected_index = self.answer_group.checkedId()
        selected_answer = self.answer_widgets[selected_index].text()
        correct_answer = self.questions[self.current_question]['correct_answer']
        
        if selected_answer == correct_answer:
            self.score += 1
            QMessageBox.information(self, "Result", "✅ Correct!")
        else:
            QMessageBox.warning(self, "Result", f"❌ Wrong! The correct answer was: {correct_answer}")
        
        self.current_question += 1
        self.show_question()
    
    def finish_quiz(self):
        result_message = (
            f"Quiz completed!\n\n"
            f"Your final score: {self.score}/{len(self.questions)}\n"
            f"Percentage: {self.score/len(self.questions)*100:.1f}%"
        )
        QMessageBox.information(self, "Quiz Results", result_message)
        self.back_button.show()
        self.submit_button.hide()
        self.parent.stacked_widget.setCurrentIndex(1)

class QuizApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Quiz Application")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Status bar for user info
        self.statusBar().showMessage("Not logged in")
        
        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create all screens
        self.login_register_widget = LoginRegisterWidget(self)
        self.main_menu_widget = MainMenuWidget(self)
        self.quiz_setup_widget = QuizSetupWidget(self)
        self.add_question_widget = AddQuestionWidget(self)
        self.view_questions_widget = ViewQuestionsWidget(self)
        self.load_json_widget = LoadJsonWidget(self)
        self.quiz_widget = QuizWidget(self)
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.login_register_widget)
        self.stacked_widget.addWidget(self.main_menu_widget)
        self.stacked_widget.addWidget(self.quiz_setup_widget)
        self.stacked_widget.addWidget(self.add_question_widget)
        self.stacked_widget.addWidget(self.view_questions_widget)
        self.stacked_widget.addWidget(self.load_json_widget)
        self.stacked_widget.addWidget(self.quiz_widget)
        
        # Show login screen first
        self.stacked_widget.setCurrentIndex(0)
        
        # Update UI based on login state
        self.update_user_status()
    
    def update_user_status(self):
        if self.current_user:
            self.statusBar().showMessage(f"Logged in as: {self.current_user}")
            self.main_menu_widget.update_welcome_message()
        else:
            self.statusBar().showMessage("Not logged in")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set a modern style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = QuizApplication()
    window.show()
    
    sys.exit(app.exec_())