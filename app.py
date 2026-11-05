from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
# 开启跨域支持
CORS(app)

# ⚠️ 数据库配置（请确保 Token 正确）
import os
from dotenv import load_dotenv

# 加载本地测试用的密码文件（线上不需要）
load_dotenv()

# 从环境变量中读取密码
DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
DATABASE_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

def get_db_url():
    return DATABASE_URL.replace("libsql://", "https://")

def turso_query(sql, params=None):
    url = get_db_url()
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    # 注意：Turso 最新 API 使用 "q" 而不是 "sql"
    body = {"statements": [{"q": sql}]}
    if params:
        body["statements"][0]["params"] = params
        
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ 数据库请求出错: {e}")
        return [{"error": str(e)}]

# 1. 渲染前端页面
@app.route('/')
def index():
    return render_template('index.html')

# 2. 初始化数据库
def init_db():
    #turso_query("DROP TABLE IF EXISTS students") 
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT,
        name TEXT,
        phone TEXT,
        school TEXT,
        homework TEXT,
        evaluation TEXT,
        score TEXT
    )
    """
    res = turso_query(create_table_sql)
    if isinstance(res, list) and len(res) > 0 and 'error' not in res[0]:
        print("✅ 数据表检查/创建成功！")
    else:
        print(f"⚠️ 建表反馈: {res}")

init_db()

# 3. API 路由
@app.route('/api/students', methods=['GET', 'POST'])
def handle_students():
    if request.method == 'GET':
        sql = "SELECT * FROM students ORDER BY id DESC"
        res = turso_query(sql)
        
        # 处理错误情况
        if isinstance(res, list) and len(res) > 0:
            if "error" in res[0]:
                return jsonify({"error": res[0]["error"]}), 500
            # 成功获取数据，返回 {"results": {"columns": [...], "rows": [...]}}
            return jsonify(res[0])
        return jsonify({"error": "数据库返回格式异常"}), 500
        
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "未接收到 JSON 数据"}), 400

        insert_sql = """
        INSERT INTO students 
        (class_name, name, phone, school, homework, evaluation, score) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            data.get('class_name', ''),
            data.get('name', ''),
            data.get('phone', ''),
            data.get('school', ''),
            data.get('homework', ''),
            data.get('evaluation', ''),
            data.get('score', '')
        ]
        
        result = turso_query(insert_sql, params)
        
        # 处理插入结果
        if isinstance(result, list) and len(result) > 0:
            if "error" in result[0]:
                print(f"❌ 插入失败: {result[0]['error']}")
                return jsonify({"error": str(result[0]['error'])}), 400
            # 插入成功
            return jsonify({"success": True})
            
        return jsonify({"error": "未知的数据库返回格式"}), 500

if __name__ == '__main__':
    # 本地运行时 debug=True，线上 Render 会自动用别的方式启动，不受影响
    app.run(debug=True)