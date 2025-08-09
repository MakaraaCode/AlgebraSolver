from logging import critical
import sys 
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from sympy import symbols, Eq, solve, simplify


class AlgebraAI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algebra AI Solver")
        self.setGeometry(300, 100, 400, 300)
        self.initUI()
        self.initDB()
        
    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Enter your algebra equation (e.g., 2*x + 3 = 7):")
        
        layout.addWidget(self.label)
        
        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)
        
        self.solve_btn = QPushButton("Solve Equation")
        self.solve_btn.clicked.connect(self.solve_equation)
        layout.addWidget(self.solve_btn)
        
        self.steps_btn = QPushButton("View Steps")
        self.steps_btn.clicked.connect(self.show_steps)
        layout.addWidget(self.steps_btn)
        
        self.result_label = QLabel("Solution/Steps:")
        layout.addWidget(self.result_label)
        
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)
        
        self.view_btn = QPushButton("View Saved Problems")
        self.view_btn.clicked.connect(self.view_saved)
        layout.addWidget(self.view_btn)
        
        self.setLayout(layout)
    
    def initDB(self):
        self.conn = sqlite3.connect("algebra_ai.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equation TEXT,
                solution TEXT
            )
        """)
        self.conn.commit()
        
    def solve_equation(self):
        equation = self.input_field.text()
        try:
            x = symbols('x')
            left, right = equation.split('=')
            eq = Eq(eval(left), eval(right))
            solution = solve(eq, x)
            
            result_text = f"x= {solution}"
            self.result_box.setText(result_text)
            
            #Save to database
            self.cursor.execute("INSERT INTO problems (equation, solution) VALUES (?,?)", (equation, str(result_text)))
            self.conn.commit()

            self.last_equation = eq # Store the last equation for steps
            self.last_solution = solution

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid equation: {e}")
    
    def show_steps(self):
        try:
            eq = self.last_equation
            x = symbols('x')
            steps = []

            # Step 1 : Original equation
            steps.append(f"Step 1 : Original equation: {eq}")

            # Step 2 : Move all terms to one side
            simplified_eq = simplify(eq.lhs - eq.rhs)
            steps.append(f"Step 2 : Move terms: {simplified_eq} = 0")

            # Step 3 : Solve for x 
            steps.append(f"Step 3 : Solve for x -> x : {self.last_solution}")

            self.result_box.setText("\n".join(steps))
            
        except AttributeError:
            QMessageBox.warning(self, "No Equation", f"Please solve an equation first before viewing steps")

    def view_saved(self):
        self.cursor.execute("SELECT * FROM problems")
        records = self.cursor.fetchall()
        
        if not records:
            QMessageBox.information(self, "No Records", "No saved pronlems found.")
            return
        
        text = ""
        for row in records:
            text += f"ID: {row[0]}\nequation: {row[1]}\nSolution: {row[2]}\n\n"
            
            self.result_box.setText(text)
            
    def closeEvent(self, event):
        self.conn.close()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window = AlgebraAI()
    Window.show()
    sys.exit(app.exec())