from flask import Flask, request, redirect, session, jsonify, render_template_string
import sqlite3
import os
import random
import time
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-super-secret-key-change-in-production")

DB_PATH = "rpg_game.db"

# DB 초기화
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 유저 테이블
        c.execute("""CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        level INTEGER DEFAULT 1,
                        exp INTEGER DEFAULT 0,
                        hp INTEGER DEFAULT 100,
                        max_hp INTEGER DEFAULT 100,
                        attack INTEGER DEFAULT 10,
                        defense INTEGER DEFAULT 5,
                        money INTEGER DEFAULT 1000,
                        weapon_level INTEGER DEFAULT 0,
                        armor_level INTEGER DEFAULT 0,
                        potions INTEGER DEFAULT 3,
                        stage INTEGER DEFAULT 1,
                        last_battle TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )""")
        
        # 몬스터 테이블
        c.execute("""CREATE TABLE monsters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        stage INTEGER,
                        hp INTEGER,
                        attack INTEGER,
                        defense INTEGER,
                        exp_reward INTEGER,
                        money_reward INTEGER
                    )""")
        
        # 기본 몬스터 데이터 삽입
        monsters_data = [
            ("슬라임", 1, 30, 8, 2, 15, 50),
            ("고블린", 1, 50, 12, 3, 25, 80),
            ("오크", 2, 80, 18, 5, 40, 120),
            ("트롤", 2, 120, 25, 8, 60, 200),
            ("드래곤", 3, 200, 40, 15, 100, 500),
            ("데몬로드", 3, 300, 60, 20, 150, 800)
        ]
        
        c.executemany("INSERT INTO monsters (name, stage, hp, attack, defense, exp_reward, money_reward) VALUES (?, ?, ?, ?, ?, ?, ?)", monsters_data)
        
        conn.commit()
        conn.close()

init_db()

# 유저 정보 가져오기
def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

# 유저 정보 업데이트
def update_user(username, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    set_clauses = []
    values = []
    
    for key, value in kwargs.items():
        if value is not None:
            set_clauses.append(f"{key}=?")
            values.append(value)
    
    if set_clauses:
        values.append(username)
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE username=?"
        c.execute(query, values)
    
    conn.commit()
    conn.close()

# 몬스터 정보 가져오기
def get_monsters_by_stage(stage):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM monsters WHERE stage=?", (stage,))
    monsters = c.fetchall()
    conn.close()
    return monsters

# 레벨업 체크
def check_levelup(user_data):
    level, exp = user_data[2], user_data[3]
    exp_needed = level * 100
    
    if exp >= exp_needed:
        new_level = level + 1
        new_exp = exp - exp_needed
        new_max_hp = user_data[5] + 20
        new_hp = new_max_hp  # 레벨업 시 체력 회복
        new_attack = user_data[6] + 5
        new_defense = user_data[7] + 3
        
        update_user(user_data[1], level=new_level, exp=new_exp, hp=new_hp, 
                   max_hp=new_max_hp, attack=new_attack, defense=new_defense)
        return True, new_level
    return False, level

# HTML 템플릿들
login_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPG 게임 - 로그인</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Arial', sans-serif;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        .title {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
    </style>
</head>
<body class="d-flex justify-content-center align-items-center vh-100">
    <div class="login-card p-5" style="width: 400px;">
        <h2 class="title text-center mb-4">⚔️ RPG 모험 게임 ⚔️</h2>
        {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
        {% endif %}
        <form method="post">
            <div class="mb-3">
                <label class="form-label">모험가 이름</label>
                <input type="text" name="username" class="form-control form-control-lg" 
                       placeholder="당신의 이름을 입력하세요" required>
            </div>
            <button type="submit" class="btn btn-primary btn-lg w-100">
                🗡️ 모험 시작하기
            </button>
        </form>
    </div>
</body>
</html>
"""

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPG 게임</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            font-family: 'Arial', sans-serif;
            min-height: 100vh;
        }
        .game-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .hp-bar {
            height: 25px;
            border-radius: 12px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.2);
        }
        .hp-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ee5a24);
            transition: width 0.5s ease;
        }
        .btn-battle {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            border: none;
            font-weight: bold;
        }
        .btn-enhance {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
            border: none;
            font-weight: bold;
        }
        .btn-shop {
            background: linear-gradient(45deg, #f093fb, #f5576c);
            border: none;
            font-weight: bold;
        }
        .battle-log {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
        .monster-card {
            background: rgba(255, 0, 0, 0.1);
            border: 2px solid rgba(255, 0, 0, 0.3);
            border-radius: 15px;
        }
        .floating-damage {
            position: absolute;
            font-size: 24px;
            font-weight: bold;
            color: #ff6b6b;
            pointer-events: none;
            animation: floatUp 1s ease-out forwards;
        }
        @keyframes floatUp {
            0% { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(-50px); }
        }
        .level-up {
            animation: levelUpGlow 2s ease-in-out;
        }
        @keyframes levelUpGlow {
            0%, 100% { box-shadow: 0 0 5px rgba(255, 215, 0, 0.5); }
            50% { box-shadow: 0 0 30px rgba(255, 215, 0, 0.8); }
        }
    </style>
</head>
<body class="p-3">
    <div class="container">
        <div class="game-container p-4 mb-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>🗡️ {{ username }}의 모험</h2>
                <a href="/logout" class="btn btn-outline-light">로그아웃</a>
            </div>
            
            <!-- 플레이어 상태 -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="stat-card p-3">
                        <h5>⚡ 플레이어 상태</h5>
                        <p><strong>레벨:</strong> <span id="level">{{ level }}</span></p>
                        <p><strong>경험치:</strong> <span id="exp">{{ exp }}</span> / <span id="exp_needed">{{ exp_needed }}</span></p>
                        <p><strong>체력:</strong> <span id="hp">{{ hp }}</span> / <span id="max_hp">{{ max_hp }}</span></p>
                        <div class="hp-bar mb-2">
                            <div class="hp-fill" id="hp-fill" style="width: {{ hp_percent }}%"></div>
                        </div>
                        <p><strong>공격력:</strong> <span id="attack">{{ attack }}</span></p>
                        <p><strong>방어력:</strong> <span id="defense">{{ defense }}</span></p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="stat-card p-3">
                        <h5>🎒 인벤토리</h5>
                        <p><strong>골드:</strong> <span id="money">{{ money }}</span> G</p>
                        <p><strong>무기 강화:</strong> +<span id="weapon_level">{{ weapon_level }}</span></p>
                        <p><strong>방어구 강화:</strong> +<span id="armor_level">{{ armor_level }}</span></p>
                        <p><strong>체력 물약:</strong> <span id="potions">{{ potions }}</span>개</p>
                        <p><strong>현재 스테이지:</strong> <span id="stage">{{ stage }}</span></p>
                    </div>
                </div>
            </div>
            
            <!-- 액션 버튼들 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <button id="battle-btn" class="btn btn-battle btn-lg w-100 mb-2">⚔️ 전투하기</button>
                </div>
                <div class="col-md-3">
                    <button id="heal-btn" class="btn btn-success btn-lg w-100 mb-2">🧪 체력 회복</button>
                </div>
                <div class="col-md-3">
                    <button id="enhance-btn" class="btn btn-enhance btn-lg w-100 mb-2">🔨 장비 강화</button>
                </div>
                <div class="col-md-3">
                    <button id="shop-btn" class="btn btn-shop btn-lg w-100 mb-2">🏪 상점</button>
                </div>
            </div>
            
            <!-- 전투 영역 -->
            <div id="battle-area" class="row mb-4" style="display: none;">
                <div class="col-12">
                    <div class="monster-card p-3 text-center">
                        <h4 id="monster-name">몬스터</h4>
                        <p>체력: <span id="monster-hp">100</span> / <span id="monster-max-hp">100</span></p>
                        <div class="hp-bar mb-2">
                            <div class="hp-fill" id="monster-hp-fill" style="width: 100%"></div>
                        </div>
                        <div class="battle-buttons">
                            <button id="attack-btn" class="btn btn-danger me-2">⚔️ 공격</button>
                            <button id="escape-btn" class="btn btn-warning">🏃 도망</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 전투 로그 -->
            <div class="battle-log p-3">
                <h5>📜 전투 로그</h5>
                <div id="log-content">
                    환영합니다! 모험을 시작하세요.
                </div>
            </div>
        </div>
    </div>

    <!-- 강화 모달 -->
    <div class="modal fade" id="enhanceModal">
        <div class="modal-dialog">
            <div class="modal-content bg-dark text-light">
                <div class="modal-header">
                    <h5 class="modal-title">🔨 장비 강화</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-6">
                            <button id="enhance-weapon" class="btn btn-primary w-100 mb-2">
                                무기 강화 (+<span id="weapon-cost">200</span>G)
                            </button>
                        </div>
                        <div class="col-6">
                            <button id="enhance-armor" class="btn btn-info w-100 mb-2">
                                방어구 강화 (+<span id="armor-cost">150</span>G)
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentMonster = null;
        let battleInProgress = false;

        // 로그 추가 함수
        function addLog(message, type = 'info') {
            const logContent = $("#log-content");
            const timestamp = new Date().toLocaleTimeString();
            const colorClass = type === 'damage' ? 'text-danger' : type === 'heal' ? 'text-success' : 'text-info';
            logContent.append(`<div class="${colorClass}">[${timestamp}] ${message}</div>`);
            logContent.scrollTop(logContent[0].scrollHeight);
        }

        // 플레이어 상태 업데이트
        function updatePlayerStats(data) {
            $("#level").text(data.level);
            $("#exp").text(data.exp);
            $("#exp_needed").text(data.level * 100);
            $("#hp").text(data.hp);
            $("#max_hp").text(data.max_hp);
            $("#attack").text(data.attack);
            $("#defense").text(data.defense);
            $("#money").text(data.money);
            $("#weapon_level").text(data.weapon_level);
            $("#armor_level").text(data.armor_level);
            $("#potions").text(data.potions);
            $("#stage").text(data.stage);
            
            const hpPercent = (data.hp / data.max_hp) * 100;
            $("#hp-fill").css("width", hpPercent + "%");
        }

        // 전투 시작
        $("#battle-btn").click(function() {
            if (battleInProgress) return;
            
            $.post("/start_battle", {}, function(data) {
                if (data.status === "ok") {
                    currentMonster = data.monster;
                    battleInProgress = true;
                    
                    $("#monster-name").text(data.monster.name);
                    $("#monster-hp").text(data.monster.hp);
                    $("#monster-max-hp").text(data.monster.hp);
                    $("#monster-hp-fill").css("width", "100%");
                    
                    $("#battle-area").fadeIn();
                    addLog(`${data.monster.name}이(가) 나타났다!`, 'info');
                } else {
                    addLog(data.message, 'damage');
                }
            });
        });

        // 공격
        $("#attack-btn").click(function() {
            if (!battleInProgress) return;
            
            $.post("/attack", {}, function(data) {
                if (data.status === "ok") {
                    // 몬스터 체력 업데이트
                    const hpPercent = (data.monster_hp / currentMonster.hp) * 100;
                    $("#monster-hp").text(data.monster_hp);
                    $("#monster-hp-fill").css("width", hpPercent + "%");
                    
                    addLog(data.message, 'damage');
                    
                    // 몬스터 죽음 체크
                    if (data.monster_dead) {
                        battleInProgress = false;
                        $("#battle-area").fadeOut();
                        addLog(data.victory_message, 'heal');
                        updatePlayerStats(data.player);
                        
                        // 레벨업 체크
                        if (data.level_up) {
                            $(".stat-card").first().addClass("level-up");
                            setTimeout(() => $(".stat-card").first().removeClass("level-up"), 2000);
                            addLog(`레벨업! 레벨 ${data.player.level}이 되었습니다!`, 'heal');
                        }
                    } else if (data.player_hp <= 0) {
                        // 플레이어 죽음
                        battleInProgress = false;
                        $("#battle-area").fadeOut();
                        addLog(data.defeat_message, 'damage');
                        updatePlayerStats(data.player);
                    } else {
                        // 플레이어 상태 업데이트
                        updatePlayerStats(data.player);
                    }
                }
            });
        });

        // 도망
        $("#escape-btn").click(function() {
            battleInProgress = false;
            $("#battle-area").fadeOut();
            addLog("전투에서 도망쳤습니다.", 'info');
        });

        // 체력 회복
        $("#heal-btn").click(function() {
            $.post("/heal", {}, function(data) {
                addLog(data.message, data.status === 'ok' ? 'heal' : 'damage');
                if (data.status === 'ok') {
                    updatePlayerStats(data.player);
                }
            });
        });

        // 강화 모달
        $("#enhance-btn").click(function() {
            const weaponCost = ({{ weapon_level }} + 1) * 200;
            const armorCost = ({{ armor_level }} + 1) * 150;
            $("#weapon-cost").text(weaponCost);
            $("#armor-cost").text(armorCost);
            $("#enhanceModal").modal('show');
        });

        // 무기 강화
        $("#enhance-weapon").click(function() {
            $.post("/enhance", { type: "weapon" }, function(data) {
                addLog(data.message, data.status === 'ok' ? 'heal' : 'damage');
                if (data.status === 'ok') {
                    updatePlayerStats(data.player);
                    $("#enhanceModal").modal('hide');
                }
            });
        });

        // 방어구 강화
        $("#enhance-armor").click(function() {
            $.post("/enhance", { type: "armor" }, function(data) {
                addLog(data.message, data.status === 'ok' ? 'heal' : 'damage');
                if (data.status === 'ok') {
                    updatePlayerStats(data.player);
                    $("#enhanceModal").modal('hide');
                }
            });
        });

        // 상점 (물약 구매)
        $("#shop-btn").click(function() {
            $.post("/shop", { item: "potion" }, function(data) {
                addLog(data.message, data.status === 'ok' ? 'heal' : 'damage');
                if (data.status === 'ok') {
                    updatePlayerStats(data.player);
                }
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    
    user = get_user(session["username"])
    if not user:
        return redirect("/login")
    
    # 사용자 데이터 파싱
    user_data = {
        'username': user[1],
        'level': user[2],
        'exp': user[3],
        'hp': user[4],
        'max_hp': user[5],
        'attack': user[6],
        'defense': user[7],
        'money': user[8],
        'weapon_level': user[9],
        'armor_level': user[10],
        'potions': user[11],
        'stage': user[12]
    }
    
    user_data['exp_needed'] = user_data['level'] * 100
    user_data['hp_percent'] = (user_data['hp'] / user_data['max_hp']) * 100
    
    return render_template_string(game_html, **user_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    error_msg = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        if not username:
            error_msg = "이름을 입력해주세요."
        else:
            user = get_user(username)
            if not user:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO users (username) VALUES (?)""", (username,))
                conn.commit()
                conn.close()
            session["username"] = username
            return redirect("/")
    
    return render_template_string(login_html, error=error_msg)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route("/start_battle", methods=["POST"])
def start_battle():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "로그인 필요"})
    
    user = get_user(session["username"])
    if user[4] <= 0:  # hp 체크
        return jsonify({"status": "fail", "message": "체력이 부족합니다. 치료를 받으세요!"})
    
    # 현재 스테이지의 몬스터 가져오기
    monsters = get_monsters_by_stage(user[12])  # stage
    if not monsters:
        return jsonify({"status": "fail", "message": "이 스테이지에는 몬스터가 없습니다."})
    
    monster = random.choice(monsters)
    monster_data = {
        "id": monster[0],
        "name": monster[1],
        "hp": monster[3],
        "max_hp": monster[3],
        "attack": monster[4],
        "defense": monster[5],
        "exp_reward": monster[6],
        "money_reward": monster[7]
    }
    
    # 세션에 현재 몬스터 정보 저장
    session["current_monster"] = monster_data
    
    return jsonify({"status": "ok", "monster": monster_data})

@app.route("/attack", methods=["POST"])
def attack():
    if "username" not in session or "current_monster" not in session:
        return jsonify({"status": "fail", "message": "전투 중이 아닙니다."})
    
    user = get_user(session["username"])
    monster = session["current_monster"]
    
    # 플레이어 공격
    player_damage = max(1, (user[6] + user[9] * 10) - monster["defense"])  # attack + weapon_level * 10
    monster["hp"] -= player_damage
    
    message = f"플레이어가 {monster['name']}에게 {player_damage} 데미지!"
    
    monster_dead = False
    level_up = False
    
    if monster["hp"] <= 0:
        # 몬스터 죽음
        monster_dead = True
        exp_gained = monster["exp_reward"]
        money_gained = monster["money_reward"]
        
        new_exp = user[3] + exp_gained
        new_money = user[8] + money_gained
        
        update_user(session["username"], exp=new_exp, money=new_money)
        
        # 레벨업 체크
        user = get_user(session["username"])
        level_up, new_level = check_levelup(user)
        
        victory_message = f"{monster['name']}을 물리쳤다! 경험치 +{exp_gained}, 골드 +{money_gained}"
        
        # 다음 스테이지 체크
        if user[2] >= user[12] * 2:  # level >= stage * 2
            new_stage = user[12] + 1
            update_user(session["username"], stage=new_stage)
            victory_message += f" | 다음 스테이지 {new_stage}로 이동!"
        
        session.pop("current_monster", None)
        user = get_user(session["username"])
        
        return jsonify({
            "status": "ok",
            "message": message,
            "monster_dead": True,
            "victory_message": victory_message,
            "level_up": level_up,
            "monster_hp": 0,
            "player": {
                "level": user[2], "exp": user[3], "hp": user[4], "max_hp": user[5],
                "attack": user[6], "defense": user[7], "money": user[8],
                "weapon_level": user[9], "armor_level": user[10], "potions": user[11], "stage": user[12]
            }
        })
    
    # 몬스터 반격
    monster_damage = max(1, monster["attack"] - (user[7] + user[10] * 5))  # defense + armor_level * 5
    new_hp = max(0, user[4] - monster_damage)
    update_user(session["username"], hp=new_hp)
    
    message += f" | {monster['name']}이 {monster_damage} 데미지로 반격!"
    
    session["current_monster"] = monster
    user = get_user(session["username"])
    
    if user[4] <= 0:
        session.pop("current_monster", None)
        return jsonify({
            "status": "ok",
            "message": message,
            "monster_dead": False,
            "defeat_message": "당신은 쓰러졌습니다... 체력을 회복하세요!",
            "monster_hp": monster["hp"],
            "player_hp": 0,
            "player": {
                "level": user[2], "exp": user[3], "hp": user[4], "max_hp": user[5],
                "attack": user[6], "defense": user[7], "money": user[8],
                "weapon_level": user[9], "armor_level": user[10], "potions": user[11], "stage": user[12]
            }
        })
    
    return jsonify({
        "status": "ok",
        "message": message,
        "monster_dead": False,
        "monster_hp": monster["hp"],
        "player": {
            "level": user[2], "exp": user[3], "hp": user[4], "max_hp": user[5],
            "attack": user[6], "defense": user[7], "money": user[8],
            "weapon_level": user[9], "armor_level": user[10], "potions": user[11], "stage": user[12]
        }
    })

@app.route("/heal", methods=["POST"])
def heal():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "로그인 필요"})
    
    user = get_user(session["username"])
    
    if user[11] <= 0:  # potions
        return jsonify({"status": "fail", "message": "체력 물약이 없습니다!"})
    
    if user[4] >= user[5]:  # hp >= max_hp
        return jsonify({"status": "fail", "message": "체력이 이미 가득합니다!"})
    
    heal_amount = min(50, user[5] - user[4])  # 최대 50 회복, max_hp 초과 불가
    new_hp = user[4] + heal_amount
    new_potions = user[11] - 1
    
    update_user(session["username"], hp=new_hp, potions=new_potions)
    user = get_user(session["username"])
    
    return jsonify({
        "status": "ok",
        "message": f"체력 물약을 사용했습니다! 체력 +{heal_amount}",
        "player": {
            "level": user[2], "exp": user[3], "hp": user[4], "max_hp": user[5],
            "attack": user[6], "defense": user[7], "money": user[8],
            "weapon_level": user[9], "armor_level": user[10], "potions": user[11], "stage": user[12]
        }
    })

@app.route("/enhance", methods=["POST"])
def enhance():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "로그인 필요"})
    
    enhance_type = request.form.get("type")
    user = get_user(session["username"])
    
    if enhance_type == "weapon":
        current_level = user[9]  # weapon_level
        cost = (current_level + 1) * 200
        success_rate = max(0.3, 0.9 - (current_level * 0.1))  # 강화 단계가 높을수록 성공률 감소
        
        if user[8] < cost:  # money
            return jsonify({"status": "fail", "message": f"골드가 부족합니다! ({cost}G 필요)"})
        
        new_money = user[8] - cost
        
        if random.random() < success_rate:
            # 성공
            new_weapon_level = current_level + 1
            new_attack = user[6] + 10  # 공격력 증가
            update_user(session["username"], money=new_money, weapon_level=new_weapon_level, attack=new_attack)
            message = f"무기 강화 성공! +{new_weapon_level} 강화 완료! 공격력이 증가했습니다!"
        else:
            # 실패
            update_user(session["username"], money=new_money)
            message = f"무기 강화 실패... 골드 {cost}G를 잃었습니다."
    
    elif enhance_type == "armor":
        current_level = user[10]  # armor_level
        cost = (current_level + 1) * 150
        success_rate = max(0.3, 0.9 - (current_level * 0.1))
        
        if user[8] < cost:  # money
            return jsonify({"status": "fail", "message": f"골드가 부족합니다! ({cost}G 필요)"})
        
        new_money = user[8] - cost
        
        if random.random() < success_rate:
            # 성공
            new_armor_level = current_level + 1
            new_defense = user[7] + 5  # 방어력 증가
            new_max_hp = user[5] + 10  # 최대 체력 증가
            update_user(session["username"], money=new_money, armor_level=new_armor_level, 
                       defense=new_defense, max_hp=new_max_hp)
            message = f"방어구 강화 성공! +{new_armor_level} 강화 완료! 방어력과 체력이 증가했습니다!"
        else:
            # 실패
            update_user(session["username"], money=new_money)
            message = f"방어구 강화 실패... 골드 {cost}G를 잃었습니다."
    
    else:
        return jsonify({"status": "fail", "message": "잘못된 강화 타입입니다."})
    
    user = get_user(session["username"])
    
    return jsonify({
        "status": "ok",
        "message": message,
        "player": {
            "level": user[2], "exp": user[3], "hp": user[4], "max_hp": user[5],
            "attack": user[6], "defense": user[7], "money": user[8],
            "weapon_level": user[9], "armor_level": user[10], "potions": user[11], "stage": user[12]
        }
    })

@app.route("/shop", methods=["POST"])
def shop():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "로그인 필요"})
    
    item = request.form.get("item")
    user = get_user(session["username"])
    
    if item == "potion":
        cost = 100
        if user[8] < cost:  # money
            return jsonify({"status": "fail", "message": f"골드가 부족합니다! ({cost}G 필요)"})
        
        new_money = user[8] - cost
        new_potions = user[11] + 1
        
        update_user(session["username"], money=new_money, potions=new_potions)
        message = f"체력 물약을 구매했습니다! (-{cost}G)"
    
    else:
        return jsonify({"status": "fail", "message": "해당 아이템을 찾을 수 없습니다."})
    
    user = get_user(session["username"])
    
    return jsonify({
        "status": "ok",
        "message": message,
        "player": {
            "level": user[2], "exp": user[3], "hp": user[4], "max_hp": user[5],
            "attack": user[6], "defense": user[7], "money": user[8],
            "weapon_level": user[9], "armor_level": user[10], "potions": user[11], "stage": user[12]
        }
    })

# Gunicorn용 WSGI 설정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

# Gunicorn 실행을 위한 application 객체
application = app
