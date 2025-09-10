from flask import Flask, render_template_string, request
import random

app = Flask(__name__)

# 게임 상태
player = {
    "gold": 1000,
    "exp": 0,
    "level": 1,
    "equipment": {"name": "기본 장비", "level": 0},
    "inventory": []
}

base_success_rate = 0.7
destroy_on_fail = True

# HTML + CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>랜덤 강화 게임</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; text-align: center; }
        h1 { color: #333; }
        .status { background: #fff; padding: 20px; margin: 20px auto; border-radius: 10px; width: 300px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .equipment, .inventory { background: #fff; padding: 15px; margin: 10px auto; border-radius: 10px; width: 300px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; background: #4CAF50; color: white; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        ul { list-style: none; padding: 0; }
        li { background: #eee; margin: 5px 0; padding: 5px; border-radius: 5px; }
        .message { font-weight: bold; color: #d9534f; margin: 15px; }
    </style>
</head>
<body>
    <h1>🎮 랜덤 강화 게임 🎮</h1>
    
    <div class="status">
        <p>레벨: {{ player.level }} | 경험치: {{ player.exp }} | 골드: {{ player.gold }}</p>
    </div>
    
    <div class="equipment">
        <h2>장비</h2>
        <p>이름: {{ player.equipment.name }} | 강화: +{{ player.equipment.level }}</p>
        <form method="post" action="/enhance">
            <button type="submit">강화 시도</button>
        </form>
    </div>

    <div class="equipment">
        <h2>사냥</h2>
        <form method="post" action="/hunt">
            <button type="submit">사냥하기</button>
        </form>
    </div>

    <div class="equipment">
        <h2>상점</h2>
        <form method="post" action="/buy">
            <button type="submit">아이템 구매 (500골드)</button>
        </form>
    </div>

    <div class="inventory">
        <h2>인벤토리</h2>
        <ul>
            {% for item in player.inventory %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>

    <div class="message">{{ message }}</div>
</body>
</html>
"""

# 강화
@app.route('/enhance', methods=['POST'])
def enhance():
    global player
    msg = ""
    rate = base_success_rate - (player['equipment']['level'] * 0.05)
    rate = max(rate, 0.1)
    if random.random() < rate:
        player['equipment']['level'] += 1
        msg = f"✨ 강화 성공! +{player['equipment']['level']} 단계 ✨"
    else:
        if destroy_on_fail:
            player['equipment'] = {"name": "기본 장비", "level": 0}
            msg = "💥 강화 실패! 장비가 파괴되었습니다 💥"
        else:
            msg = "❌ 강화 실패!"
    return render_template_string(HTML_TEMPLATE, player=player, message=msg)

# 사냥
@app.route('/hunt', methods=['POST'])
def hunt():
    global player
    gold_earned = random.randint(50, 200)
    exp_earned = random.randint(10, 50)
    player['gold'] += gold_earned
    player['exp'] += exp_earned
    msg = f"⚔️ 사냥 완료! 골드 +{gold_earned}, 경험치 +{exp_earned}"
    if player['exp'] >= player['level'] * 100:
        player['exp'] -= player['level'] * 100
        player['level'] += 1
        msg += f" 🎉 레벨업! 새로운 레벨: {player['level']} 🎉"
    return render_template_string(HTML_TEMPLATE, player=player, message=msg)

# 상점
@app.route('/buy', methods=['POST'])
def buy():
    global player
    if player['gold'] >= 500:
        player['gold'] -= 500
        item_name = f"아이템{len(player['inventory'])+1}"
        player['inventory'].append(item_name)
        msg = f"🛒 {item_name}을(를) 구매했습니다!"
    else:
        msg = "💰 골드가 부족합니다!"
    return render_template_string(HTML_TEMPLATE, player=player, message=msg)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, player=player, message="")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)