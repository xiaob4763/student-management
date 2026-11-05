from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            班级 TEXT,
            姓名 TEXT,
            电话 TEXT,
            学校 TEXT,
            作业情况 TEXT,
            课堂评价 TEXT,
            测试成绩 TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


class StudentIn(BaseModel):
    班级: str
    姓名: str
    电话: str
    学校: str
    作业情况: str = ""
    课堂评价: str = ""
    测试成绩: str = ""


@app.get("/students")
def list_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/students")
def add_student(student: StudentIn):
    conn = get_db()
    cursor = conn.execute(
        """
        INSERT INTO students (班级, 姓名, 电话, 学校, 作业情况, 课堂评价, 测试成绩)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student.班级,
            student.姓名,
            student.电话,
            student.学校,
            student.作业情况,
            student.课堂评价,
            student.测试成绩,
        ),
    )
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid, "message": "添加成功"}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}