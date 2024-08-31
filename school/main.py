from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    grade: int

def setup_database():
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade INTEGER
            )
            """
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database setup error: {e}")

setup_database()

@app.get('/students/')
def read_students():
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students;")
        rows = cursor.fetchall()
        conn.close()
        students = [{"id": row[0], "name": row[1], "grade": row[2]} for row in rows]
        return {"students": students}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Failed to fetch students.")

@app.post('/students/')
async def create_students(student: Student):
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students(name, grade) VALUES (?, ?);",
            (student.name, student.grade)
        )
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"message": "Student added successfully", "id": student_id}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Failed to create student.")

@app.put('/students/{st_id}')
async def update_students(st_id: int, student: Student):
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, grade = ? WHERE id = ?;",
            (student.name, student.grade, st_id)
        )
        conn.commit()
        conn.close()
        return {"message": "Student updated successfully", "id": st_id}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Failed to update student.")

@app.delete('/students/{st_id}')
async def delete_students(st_id: int):
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?;", (st_id,))
        conn.commit()
        conn.close()
        return {"message": "Student deleted successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Failed to delete student.")
