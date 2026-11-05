import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "students.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()

init_db()

def get_all_students():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def add_student(班级, 姓名, 电话, 学校, 作业情况, 课堂评价, 测试成绩):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (班级, 姓名, 电话, 学校, 作业情况, 课堂评价, 测试成绩) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (班级, 姓名, 电话, 学校, 作业情况, 课堂评价, 测试成绩))
    conn.commit()
    conn.close()

def delete_student(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

st.title("🏫 培训机构学生管理系统")
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("📝 录入信息")
    班级 = st.text_input("班级", "")
    姓名 = st.text_input("姓名", "")
    电话 = st.text_input("电话", "")
    学校 = st.text_input("学校", "")
    作业情况 = st.text_input("作业完成情况", "例如：已完成")
    课堂评价 = st.text_input("课堂评价", "例如：积极互动")
    测试成绩 = st.text_input("测试成绩", "例如：95分")

    if st.button("添加学生"):
        if 班级 and 姓名 and 电话 and 学校:
            add_student(班级, 姓名, 电话, 学校, 作业情况, 课堂评价, 测试成绩)
            st.success("添加成功！页面即将刷新。")
            st.rerun()
        else:
            st.error("请至少填写班级、姓名、电话和学校！")

    st.divider()
    st.subheader("🗑️ 删除数据")
    delete_id = st.number_input("输入要删除的学生ID", min_value=1, step=1)
    if st.button("确认删除", type="primary"):
        delete_student(delete_id)
        st.success(f"ID为 {delete_id} 的学生已删除！")
        st.rerun()

with col2:
    st.subheader("📊 学生信息列表")
    df = get_all_students()
    if not df.empty:
        display_df = df.drop(columns=['id'])
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("目前还没有学生数据，请从左侧添加。")
