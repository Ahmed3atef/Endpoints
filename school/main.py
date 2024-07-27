from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    id: int
    name: str
    grade: int
    

students = [
    Student(id=1, name="Ahmed Atef", grade=5),
    Student(id=2, name="Donia Esam", grade=6),
]

@app.get('/students/')
def read_students():
    return students

@app.post('/students/')
def create_students(New_students: Student):
    students.append(New_students)
    return New_students

@app.put('/students/{st_id}')
def update_students(st_id:int, updated_student:Student):
    for index , student in enumerate(students):
        if student.id == st_id:
            students[index] = updated_student
            return updated_student
    return {'error': 'Student not found!'}

@app.delete('/students/{st_id}')
def delete_students(st_id:int):
    for index, student in enumerate(students):
        if student.id == st_id:
            del students[index]
            return {"message":"Student deleted"}
    return {'error': "student not found!"}