from database import SessionLocal
from models import Student, Paper, Question, AnswerScript, QuestionMark
from sqlalchemy import text
import random

def seed_database():
    db = SessionLocal()
    
    print("Wiping data and resetting IDs...")
    db.execute(text("TRUNCATE TABLE question_marks RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE answer_scripts RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE questions RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE papers RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE students RESTART IDENTITY CASCADE;"))
    db.commit()

    print("Inserting 30 students...")
    students = []
    student_counter = 1
    for section in ['A', 'B', 'C']:
        for i in range(1, 11):
            student = Student(
                name=f'Student_{section}_{i}',
                email=f'student{student_counter}@test.com', 
                roll_number=i,
                class_name='10',
                section=section,
                admission_number=f'ADM_{section}_{i}'
            )
            students.append(student)
            student_counter += 1
            
    db.add_all(students)
    db.commit()

    print("Inserting Papers and Questions...")
    math_paper = Paper(name='Math Midterm', total_max_marks=100)
    science_paper = Paper(name='Science Final', total_max_marks=100)
    db.add_all([math_paper, science_paper])
    db.commit()

    math_questions = []
    for i in range(1, 6):
        q = Question(paper_id=math_paper.id, question_number=i, max_marks=20, choice_group=None)
        math_questions.append(q)
        db.add(q)
        
    science_questions = []
    science_questions.append(Question(paper_id=science_paper.id, question_number=1, max_marks=25, choice_group='Group A'))
    science_questions.append(Question(paper_id=science_paper.id, question_number=2, max_marks=25, choice_group='Group A'))
    science_questions.append(Question(paper_id=science_paper.id, question_number=3, max_marks=25, choice_group='Group B'))
    science_questions.append(Question(paper_id=science_paper.id, question_number=4, max_marks=25, choice_group='Group B'))
    for q in science_questions:
        db.add(q)
        
    db.commit() 

    print("Creating Scripts and Assigning Marks...")
    for student in students:
        script = AnswerScript(paper_id=math_paper.id, student_id=student.id)
        db.add(script)
        db.commit()

        for q in math_questions:
            mark = random.randint(5, 20)
            qm = QuestionMark(script_id=script.id, question_id=q.id, marks_obtained=mark)
            db.add(qm)
    
    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()