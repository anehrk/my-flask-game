from flask import Flask, request, render_template_string
import sqlite3
import random
import os

app = Flask(__name__)
DB_FILE = "game2.db"

# ------------------------
# DB 초기화
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            gold INTEGER DEFAULT 1000,
            level INTEGER DEFAULT 1,
            item_potion INTEGER DEFAULT 3
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------------
# HTML 템플릿
# ------------------------
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>게임 로그인</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f2f2f2; text-align: center; }
        form { margin-top: 100px; }
        input { padding: 8px; font-size: 16px; }
        button { padding: 8px 16px; font-size: 16px; margin-left: 10px; cursor: pointer; }
        h2 { color: #333; }
    </style>
</head>
<body>
<h2>게임 로그인</h2>
<form method="post" action="/login">
    아이디: <input type="text" name="user_id" required>
    <button type="submit">로그인</button>
</form>
</body>
</html>
"""

GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>게임 화면</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #e6f7ff; text-align: center; }
        .container { margin-top: 50px; }
        button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; border-radius: 5px; }
        .success { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
        .status { margin: 20px 0; font-size: 18px; }
        .card { display: inline-block; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h2>{{user_id}}님 환영합니다!</h2>
        <div class="status">
            <p>레벨: {{level}}</p>
            <p>골드: {{gold}}</p>
            <p>포션: {{item_potion}}</p>
        </div>

        <form method="post" action="/enhance">
            <input type="hidden" name="user_id" value="{{user_id}}">
            <button type="submit">강화 (골드 100 소모)</button>
        </form>

        <form method="post" action="/use_item">
            <input type="hidden" name="user_id" value="{{user_id}}">
            <button type="submit">포션 사용 (레벨 +1, 1개 소모)</button>
        </form>

        <form method="get" action="/">
            <button>로그아웃</button>
        </form>

        {% if message %}
            <p class="{{ 'success' if '성공' in message or '사용' in message else 'fail' }}">{{message}}</p>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

# ------------------------
# 유저 데이터 가져오기
# ------------------------
def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT gold, level, item_potion FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"gold": row[0], "level": row[1], "item_potion": row[2]}
    return None

# ------------------------
# 라우팅
# ------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template_string(LOGIN_HTML)

@app.route("/login", methods=["POST"])
def login():
    user_id = request.form["user_id"].strip()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(id) VALUES(?)", (user_id,))
    conn.commit()
    conn.close()
    user = get_user(user_id)
    return render_template_string(GAME_HTML, user_id=user_id, **user, message="로그인 성공!")

@app.route("/enhance", methods=["POST"])
def enhance():
    user_id = request.form["user_id"]
    user = get_user(user_id)
    message = ""
    if user["gold"] < 100:
        message = "골드가 부족합니다!"
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET gold = gold - 100 WHERE id=?", (user_id,))
        if random.random() < 0.7:
            c.execute("UPDATE users SET level = level + 1 WHERE id=?", (user_id,))
            message = "강화 성공!"
        else:
            message = "강화 실패..."
        conn.commit()
        conn.close()
    user = get_user(user_id)
    return render_template_string(GAME_HTML, user_id=user_id, **user, message=message)

@app.route("/use_item", methods=["POST"])
def use_item():
    user_id = request.form["user_id"]
    user = get_user(user_id)
    message = ""
    if user["item_potion"] <= 0:
        message = "포션이 없습니다!"
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET level = level + 1, item_potion = item_potion - 1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        message = "포션 사용! 레벨 +1"
    user = get_user(user_id)
    return render_template_string(GAME_HTML, user_id=user_id, **user, message=message)

# ------------------------
# 앱 실행
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
