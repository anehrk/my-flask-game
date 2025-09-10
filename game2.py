"""
승진 강화 게임 - 웹(Flask) 버전 + 향상된 tkinter 데스크탑 버전
파일명: 승진게임_enhanced_version.py

새로운 기능들:
1) 수동 클릭으로 돈벌기 (클릭당 수익)
2) 수익 증가 아이템들 (자동 수익 부스터)
3) 복권 시스템 (여러 등급의 복권)
4) 도박 시스템 (배율 게임, 룰렛)
5) 투자 시스템 (시간에 따른 수익)
6) 퀘스트/업적 시스템

사용법 (웹):
- 필요: Python 3.8+
- 설치: pip install Flask
- 실행: python 승진게임_enhanced_version.py --web
- 접속: http://127.0.0.1:5000

사용법 (데스크탑):
- 실행: python 승진게임_enhanced_version.py --tk
"""

import sys

RUN_WEB = '--web' in sys.argv
RUN_TK = '--tk' in sys.argv

if not (RUN_WEB or RUN_TK):
    print("실행 모드를 지정하세요: --web (Flask 웹), 또는 --tk (tkinter 데스크탑)")
    print("예: python 승진게임_enhanced_version.py --web")
    sys.exit(0)

# ------------------------
# Flask 웹서버 (enhanced version)
# ------------------------
if RUN_WEB:
    from flask import Flask, render_template_string

    app = Flask(__name__)

    ENHANCED_HTML = r"""
    <!doctype html>
    <html lang="ko">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>승진 강화 게임 Enhanced (웹)</title>
      <style>
        :root{--bg:#0f172a;--card:#0b1220;--accent:#60a5fa;--success:#34d399;--danger:#fb7185;--warning:#fbbf24;--purple:#a855f7}
        html,body{height:100%;margin:0;font-family:Inter, Roboto, Arial;background:linear-gradient(180deg,#071024 0%, #081227 100%);color:#e6eef8}
        .wrap{max-width:1200px;margin:20px auto;padding:20px;border-radius:14px;background:rgba(255,255,255,0.03);box-shadow:0 8px 30px rgba(2,6,23,0.6)}
        h1,h2{margin:0 0 12px;color:#60a5fa}
        h1{font-size:24px} h2{font-size:18px;margin-top:20px}
        .top-row{display:flex;gap:12px;align-items:flex-start;margin-bottom:20px}
        .stat{background:rgba(255,255,255,0.02);padding:12px;border-radius:10px;min-width:140px;text-align:center}
        .big{font-size:20px;font-weight:700}
        .tabs{display:flex;gap:8px;margin:16px 0}
        .tab{padding:8px 16px;border-radius:8px;border:0;background:rgba(255,255,255,0.06);color:#cfe6ff;cursor:pointer}
        .tab.active{background:var(--accent);color:#04203a}
        .tab-content{display:none;background:rgba(255,255,255,0.02);padding:16px;border-radius:12px;margin:12px 0}
        .tab-content.active{display:block}
        .buttons{display:flex;gap:8px;flex-wrap:wrap}
        button{padding:8px 14px;border-radius:8px;border:0;background:var(--accent);color:#04203a;font-weight:600;cursor:pointer;box-shadow:0 4px 12px rgba(96,165,250,0.12);transition:all 0.2s}
        button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(96,165,250,0.2)}
        button.success{background:var(--success)}
        button.danger{background:var(--danger)}
        button.warning{background:var(--warning)}
        button.purple{background:var(--purple);color:white}
        button.muted{background:rgba(255,255,255,0.06);color:#cfe6ff}
        button:disabled{opacity:0.5;cursor:not-allowed}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:12px 0}
        .card{background:rgba(255,255,255,0.02);padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,0.05)}
        .card h3{margin:0 0 8px;font-size:14px;font-weight:700}
        .money-click{position:fixed;pointer-events:none;font-weight:700;color:var(--success);animation:moneyFloat 1.5s ease-out forwards;z-index:1000}
        @keyframes moneyFloat{0%{opacity:1;transform:translateY(0)}100%{opacity:0;transform:translateY(-60px)}}
        .click-area{width:200px;height:200px;border-radius:50%;background:linear-gradient(45deg,var(--accent),var(--purple));margin:20px auto;display:flex;align-items:center;justify-content:center;cursor:pointer;user-select:none;font-size:24px;transition:transform 0.1s;box-shadow:0 8px 32px rgba(96,165,250,0.3)}
        .click-area:hover{transform:scale(1.05)}
        .click-area:active{transform:scale(0.95)}
        .progress-bar{background:rgba(255,255,255,0.1);border-radius:10px;overflow:hidden;height:8px;margin:8px 0}
        .progress-fill{background:linear-gradient(90deg,var(--accent),var(--success));height:100%;transition:width 0.3s}
        .flash{animation:flash 0.4s ease-out}
        @keyframes flash{0%{transform:scale(1)}50%{transform:scale(1.05)}100%{transform:scale(1)}}
        .roulette{width:200px;height:200px;border-radius:50%;background:conic-gradient(from 0deg, #ff6b6b 0deg 60deg, #4ecdc4 60deg 120deg, #45b7d1 120deg 180deg, #96ceb4 180deg 240deg, #ffeaa7 240deg 300deg, #dda0dd 300deg 360deg);margin:0 auto;position:relative;border:4px solid white}
        .roulette-pointer{position:absolute;top:-10px;left:50%;transform:translateX(-50%);width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:16px solid white}
        .spinning{animation:spin 2s ease-out}
        @keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(1800deg)}}
        #message{margin:16px 0;padding:12px;text-align:center;font-weight:700;border-radius:8px;min-height:20px}
        .confetti-container{height:100px;overflow:hidden;position:relative}
        canvas{position:absolute;left:0;top:0;width:100%;height:100%}
      </style>
    </head>
    <body>
    <div class="wrap">
      <h1>🏢 승진 강화 게임 Enhanced (웹)</h1>
      
      <!-- 상단 통계 -->
      <div class="top-row">
        <div class="stat">
          <div style="font-size:12px;opacity:0.7">💰 총 자산</div>
          <div id="money" class="big">0</div>
          <div style="font-size:12px;opacity:0.6">초당: <span id="income">10</span></div>
          <div style="font-size:12px;opacity:0.6">클릭당: <span id="clickValue">1</span></div>
        </div>
        <div class="stat">
          <div style="font-size:12px;opacity:0.7">🏢 현재 직급</div>
          <div id="rank" class="big">인턴</div>
          <div style="font-size:12px;opacity:0.6">레벨: <span id="level">0</span></div>
        </div>
        <div class="stat">
          <div style="font-size:12px;opacity:0.7">🎯 승진 정보</div>
          <div style="font-size:14px">확률: <span id="prob">70%</span></div>
          <div style="font-size:14px">비용: <span id="cost">100</span></div>
        </div>
        <div class="stat">
          <div style="font-size:12px;opacity:0.7">🎲 도박 통계</div>
          <div style="font-size:14px">승리: <span id="gamblingWins">0</span></div>
          <div style="font-size:14px">패배: <span id="gamblingLoses">0</span></div>
        </div>
      </div>

      <!-- 탭 메뉴 -->
      <div class="tabs">
        <button class="tab active" onclick="switchTab('main')">🏢 승진</button>
        <button class="tab" onclick="switchTab('income')">💰 수익</button>
        <button class="tab" onclick="switchTab('lottery')">🎟️ 복권</button>
        <button class="tab" onclick="switchTab('gambling')">🎲 도박</button>
        <button class="tab" onclick="switchTab('investment')">📈 투자</button>
        <button class="tab" onclick="switchTab('achievements')">🏆 업적</button>
      </div>

      <!-- 메인 승진 탭 -->
      <div id="main" class="tab-content active">
        <div style="display:flex;gap:20px;align-items:flex-start">
          <div style="flex:1">
            <div class="buttons" style="margin-bottom:16px">
              <button id="promote">🚀 승진 시도</button>
              <button id="auto" class="muted">자동 OFF</button>
            </div>
            <div class="grid">
              <div class="card">
                <h3>📈 확률 부스터 (+10%)</h3>
                <p style="font-size:12px;opacity:0.7">1회용, 다음 승진 시도 확률 증가</p>
                <div>가격: <span id="boostCost">500</span> | 보유: <span id="boostOwned">0</span></div>
                <button id="buyBoost" style="margin-top:8px">구매</button>
              </div>
              <div class="card">
                <h3>🛡️ 강등 방지</h3>
                <p style="font-size:12px;opacity:0.7">1회용, 승진 실패 시 강등 방지</p>
                <div>가격: <span id="protectCost">1000</span> | 보유: <span id="protectOwned">0</span></div>
                <button id="buyProtect" style="margin-top:8px">구매</button>
              </div>
            </div>
          </div>
          <div style="text-align:center">
            <div class="click-area" id="clickArea" onclick="clickMoney()">💰<br>클릭!</div>
            <p style="font-size:12px;opacity:0.7;margin-top:8px">클릭해서 돈을 벌어보세요!</p>
          </div>
        </div>
      </div>

      <!-- 수익 증대 탭 -->
      <div id="income" class="tab-content">
        <h2>💰 수익 증대 아이템</h2>
        <div class="grid">
          <div class="card">
            <h3>☕ 커피머신</h3>
            <p style="font-size:12px">초당 수익 +5</p>
            <div>가격: <span id="coffeePrice">200</span> | 보유: <span id="coffeeOwned">0</span></div>
            <button onclick="buyIncomeItem('coffee')" style="margin-top:8px">구매</button>
          </div>
          <div class="card">
            <h3>💻 고성능 PC</h3>
            <p style="font-size:12px">초당 수익 +20</p>
            <div>가격: <span id="pcPrice">1000</span> | 보유: <span id="pcOwned">0</span></div>
            <button onclick="buyIncomeItem('pc')" style="margin-top:8px">구매</button>
          </div>
          <div class="card">
            <h3>🏠 사무실</h3>
            <p style="font-size:12px">초당 수익 +100</p>
            <div>가격: <span id="officePrice">5000</span> | 보유: <span id="officeOwned">0</span></div>
            <button onclick="buyIncomeItem('office')" style="margin-top:8px">구매</button>
          </div>
          <div class="card">
            <h3>🏢 빌딩</h3>
            <p style="font-size:12px">초당 수익 +500</p>
            <div>가격: <span id="buildingPrice">25000</span> | 보유: <span id="buildingOwned">0</span></div>
            <button onclick="buyIncomeItem('building')" style="margin-top:8px">구매</button>
          </div>
          <div class="card">
            <h3>🤖 AI 어시스턴트</h3>
            <p style="font-size:12px">클릭당 수익 +2</p>
            <div>가격: <span id="aiPrice">800</span> | 보유: <span id="aiOwned">0</span></div>
            <button onclick="buyIncomeItem('ai')" style="margin-top:8px">구매</button>
          </div>
          <div class="card">
            <h3>⚡ 에너지 드링크</h3>
            <p style="font-size:12px">클릭당 수익 +10</p>
            <div>가격: <span id="energyPrice">3000</span> | 보유: <span id="energyOwned">0</span></div>
            <button onclick="buyIncomeItem('energy')" style="margin-top:8px">구매</button>
          </div>
        </div>
      </div>

      <!-- 복권 탭 -->
      <div id="lottery" class="tab-content">
        <h2>🎟️ 복권 시스템</h2>
        <div class="grid">
          <div class="card">
            <h3>🎫 기본 복권</h3>
            <p style="font-size:12px">1등: 10,000 (1%), 2등: 1,000 (5%), 3등: 100 (20%)</p>
            <button onclick="buyLottery('basic', 50)" class="warning">50원으로 구매</button>
          </div>
          <div class="card">
            <h3>🎟️ 프리미엄 복권</h3>
            <p style="font-size:12px">1등: 100,000 (2%), 2등: 10,000 (8%), 3등: 1,000 (25%)</p>
            <button onclick="buyLottery('premium', 500)" class="purple">500원으로 구매</button>
          </div>
          <div class="card">
            <h3>🏆 메가 복권</h3>
            <p style="font-size:12px">1등: 1,000,000 (0.1%), 2등: 50,000 (1%), 3등: 5,000 (10%)</p>
            <button onclick="buyLottery('mega', 2000)" class="danger">2,000원으로 구매</button>
          </div>
        </div>
        <div style="margin-top:16px">
          <div>🎉 복권 당첨 통계: 총 당첨금 <span id="lotteryWinnings">0</span>원</div>
        </div>
      </div>

      <!-- 도박 탭 -->
      <div id="gambling" class="tab-content">
        <h2>🎲 도박장</h2>
        
        <!-- 배율 게임 -->
        <div class="card" style="margin-bottom:16px">
          <h3>🎯 배율 게임</h3>
          <p>베팅액의 2배 (50%), 3배 (25%), 5배 (10%), 10배 (5%) 또는 전액 손실 (10%)</p>
          <div style="margin:8px 0">
            <input type="number" id="betAmount" min="100" value="1000" style="padding:4px;border-radius:4px;border:1px solid #ccc;width:100px">
            <button onclick="playMultiplierGame()" class="danger" style="margin-left:8px">도박하기</button>
          </div>
        </div>

        <!-- 룰렛 -->
        <div class="card">
          <h3>🎡 룰렛</h3>
          <div style="text-align:center;margin:16px 0">
            <div class="roulette" id="roulette">
              <div class="roulette-pointer"></div>
            </div>
            <div style="margin-top:12px">
              <input type="number" id="rouletteBet" min="500" value="2000" style="padding:4px;border-radius:4px;border:1px solid #ccc;width:100px">
              <button onclick="spinRoulette()" class="purple" style="margin-left:8px">룰렛 돌리기</button>
            </div>
            <p style="font-size:12px;margin-top:8px">빨강(1배), 파랑(0.5배), 연두(1.5배), 민트(0배), 노랑(3배), 보라(5배)</p>
          </div>
        </div>
      </div>

      <!-- 투자 탭 -->
      <div id="investment" class="tab-content">
        <h2>📈 투자 시스템</h2>
        <div class="grid">
          <div class="card">
            <h3>🏦 은행 예금</h3>
            <p style="font-size:12px">30초마다 10% 수익 (안전)</p>
            <div style="margin:8px 0">
              <input type="number" id="bankInvest" min="1000" value="5000" style="padding:4px;width:100px">
              <button onclick="invest('bank')" class="success">투자</button>
            </div>
            <div>투자중: <span id="bankInvestment">0</span>원</div>
            <div class="progress-bar">
              <div class="progress-fill" id="bankProgress" style="width:0%"></div>
            </div>
          </div>
          <div class="card">
            <h3>📊 주식</h3>
            <p style="font-size:12px">60초마다 30% 수익 또는 20% 손실</p>
            <div style="margin:8px 0">
              <input type="number" id="stockInvest" min="2000" value="10000" style="padding:4px;width:100px">
              <button onclick="invest('stock')" class="warning">투자</button>
            </div>
            <div>투자중: <span id="stockInvestment">0</span>원</div>
            <div class="progress-bar">
              <div class="progress-fill" id="stockProgress" style="width:0%"></div>
            </div>
          </div>
          <div class="card">
            <h3>🚀 암호화폐</h3>
            <p style="font-size:12px">120초마다 100% 수익 또는 50% 손실</p>
            <div style="margin:8px 0">
              <input type="number" id="cryptoInvest" min="5000" value="20000" style="padding:4px;width:100px">
              <button onclick="invest('crypto')" class="danger">투자</button>
            </div>
            <div>투자중: <span id="cryptoInvestment">0</span>원</div>
            <div class="progress-bar">
              <div class="progress-fill" id="cryptoProgress" style="width:0%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 업적 탭 -->
      <div id="achievements" class="tab-content">
        <h2>🏆 업적 시스템</h2>
        <div class="grid" id="achievementsList">
          <!-- 업적들이 동적으로 추가됨 -->
        </div>
      </div>

      <div id="message"></div>

      <div class="confetti-container">
        <canvas id="confettiCanvas"></canvas>
      </div>
    </div>

    <script>
    // 게임 데이터
    const ranks = ["인턴","사원","대리","과장","부장","전무","사장","회장","명예회장","재벌총수","세계재벌왕"]
    const probs = [0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.08,0.05,0.03]
    const baseCost = 100, baseIncome = 10

    let gameState = {
      level: 0, money: 0, income: baseIncome, clickValue: 1,
      boostOwned: 0, protectOwned: 0, autoOn: false,
      gamblingWins: 0, gamblingLoses: 0, lotteryWinnings: 0,
      // 수익 아이템
      incomeItems: {
        coffee: {owned: 0, price: 200, income: 5, priceMultiplier: 1.15},
        pc: {owned: 0, price: 1000, income: 20, priceMultiplier: 1.2},
        office: {owned: 0, price: 5000, income: 100, priceMultiplier: 1.25},
        building: {owned: 0, price: 25000, income: 500, priceMultiplier: 1.3},
        ai: {owned: 0, price: 800, clickBonus: 2, priceMultiplier: 1.15},
        energy: {owned: 0, price: 3000, clickBonus: 10, priceMultiplier: 1.2}
      },
      // 투자
      investments: {
        bank: {amount: 0, startTime: 0, duration: 30000, rate: 0.1, risk: 0},
        stock: {amount: 0, startTime: 0, duration: 60000, rate: 0.3, risk: 0.2},
        crypto: {amount: 0, startTime: 0, duration: 120000, rate: 1.0, risk: 0.5}
      },
      // 업적
      achievements: {
        firstClick: {name: "첫 클릭", desc: "처음으로 돈을 클릭해서 벌기", completed: false, reward: 100},
        promotion1: {name: "첫 승진", desc: "처음으로 승진하기", completed: false, reward: 500},
        millionaire: {name: "백만장자", desc: "100만원 모으기", completed: false, reward: 50000},
        gamblingKing: {name: "도박왕", desc: "도박에서 10번 승리하기", completed: false, reward: 10000},
        lotteryWinner: {name: "복권 당첨자", desc: "복권에서 총 10만원 당첨", completed: false, reward: 20000},
        ceoLevel: {name: "CEO 도달", desc: "사장 직급에 도달하기", completed: false, reward: 100000}
      }
    }

    // 코스트 계산 함수들
    function calcPromotionCost(l){ return Math.floor(baseCost * Math.pow(2,l)) }
    function calcBoostCost(l){ return Math.floor(500 * Math.pow(1.9, l)) }
    function calcProtectCost(l){ return Math.floor(1000 * Math.pow(1.9, l)) }

    // UI 업데이트
    function updateUI(){
      document.getElementById('money').textContent = Math.floor(gameState.money)
      document.getElementById('income').textContent = gameState.income
      document.getElementById('clickValue').textContent = gameState.clickValue
      document.getElementById('rank').textContent = ranks[gameState.level]
      document.getElementById('level').textContent = gameState.level
      document.getElementById('gamblingWins').textContent = gameState.gamblingWins
      document.getElementById('gamblingLoses').textContent = gameState.gamblingLoses
      document.getElementById('lotteryWinnings').textContent = Math.floor(gameState.lotteryWinnings)
      
      if(gameState.level < ranks.length - 1){
        document.getElementById('prob').textContent = Math.round(probs[gameState.level]*100) + '%'
        document.getElementById('cost').textContent = calcPromotionCost(gameState.level)
      } else {
        document.getElementById('prob').textContent = '최고'
        document.getElementById('cost').textContent = '---'
      }
      
      document.getElementById('boostCost').textContent = calcBoostCost(gameState.level)
      document.getElementById('protectCost').textContent = calcProtectCost(gameState.level)
      document.getElementById('boostOwned').textContent = gameState.boostOwned
      document.getElementById('protectOwned').textContent = gameState.protectOwned
      
      // 수익 아이템 UI 업데이트
      for(let [key, item] of Object.entries(gameState.incomeItems)){
        const priceEl = document.getElementById(key + 'Price')
        const ownedEl = document.getElementById(key + 'Owned')
        if(priceEl) priceEl.textContent = Math.floor(item.price)
        if(ownedEl) ownedEl.textContent = item.owned
      }
      
      updateAchievements()
    }

    // 수익 계산
    function calculateIncome(){
      let income = baseIncome * Math.pow(2, gameState.level)
      for(let item of Object.values(gameState.incomeItems)){
        if(item.income) income += item.income * item.owned
      }
      gameState.income = income
    }

    function calculateClickValue(){
      let clickValue = 1 + Math.floor(gameState.level / 2)
      for(let item of Object.values(gameState.incomeItems)){
        if(item.clickBonus) clickValue += item.clickBonus * item.owned
      }
      gameState.clickValue = clickValue
    }

    // 클릭으로 돈 벌기
    function clickMoney(){
      gameState.money += gameState.clickValue
      showMoneyFloat(gameState.clickValue)
      checkAchievement('firstClick')
      updateUI()
    }

    function showMoneyFloat(amount){
      const clickArea = document.getElementById('clickArea')
      const rect = clickArea.getBoundingClientRect()
      const floater = document.createElement('div')
      floater.className = 'money-click'
      floater.textContent = '+' + amount
      floater.style.left = (rect.left + rect.width/2) + 'px'
      floater.style.top = rect.top + 'px'
      document.body.appendChild(floater)
      setTimeout(() => document.body.removeChild(floater), 1500)
    }

    // 탭 전환
    function switchTab(tabName){
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'))
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'))
      event.target.classList.add('active')
      document.getElementById(tabName).classList.add('active')
    }

    // 승진
    function promote(){
      if(gameState.level >= ranks.length -1){ showMessage('최고 직급입니다!', 'success'); return }
      const cost = calcPromotionCost(gameState.level)
      if(gameState.money < cost){ showMessage('돈이 부족합니다!', 'fail'); return }
      
      gameState.money -= cost
      let chance = probs[gameState.level]
      if(gameState.boostOwned > 0){ chance += 0.10; gameState.boostOwned-- }

      const success = Math.random() < chance
      if(success){
        gameState.level++
        calculateIncome()
        calculateClickValue()
        showMessage('✅ 승진 성공! ' + ranks[gameState.level], 'success')
        burstConfetti()
        checkAchievement('promotion1')
        if(gameState.level >= 6) checkAchievement('ceoLevel') // 사장 = index 6
      } else {
        if(gameState.protectOwned > 0){
          gameState.protectOwned--
          showMessage('❌ 승진 실패! (아이템으로 강등 방지)', 'fail')
        } else {
          if(gameState.level > 0){
            gameState.level--
            calculateIncome()
            calculateClickValue()
            showMessage('❌ 승진 실패! 한 단계 강등', 'fail')
          } else {
            showMessage('❌ 승진 실패! (강등 없음)', 'fail')
          }
        }
        shakeScreen()
      }
      updateUI()
    }

    // 수익 아이템 구매
    function buyIncomeItem(itemName){
      const item = gameState.incomeItems[itemName]
      if(gameState.money >= item.price){
        gameState.money -= item.price
        item.owned++
        item.price = Math.floor(item.price * item.priceMultiplier)
        calculateIncome()
        calculateClickValue()
        showMessage(`${itemName} 구매 완료!`, 'success')
        updateUI()
      } else {
        showMessage('돈이 부족합니다!', 'fail')
      }
    }

    // 복권 시스템
    function buyLottery(type, cost){
      if(gameState.money < cost){
        showMessage('돈이 부족합니다!', 'fail')
        return
      }
      
      gameState.money -= cost
      const rand = Math.random() * 100
      let prize = 0, message = ''
      
      if(type === 'basic'){
        if(rand < 1){ prize = 10000; message = '🎉 기본복권 1등 당첨! +10,000원' }
        else if(rand < 6){ prize = 1000; message = '🎊 기본복권 2등 당첨! +1,000원' }
        else if(rand < 26){ prize = 100; message = '🎈 기본복권 3등 당첨! +100원' }
        else { message = '😢 기본복권 꽝!' }
      } else if(type === 'premium'){
        if(rand < 2){ prize = 100000; message = '🎉 프리미엄복권 1등 당첨! +100,000원' }
        else if(rand < 10){ prize = 10000; message = '🎊 프리미엄복권 2등 당첨! +10,000원' }
        else if(rand < 35){ prize = 1000; message = '🎈 프리미엄복권 3등 당첨! +1,000원' }
        else { message = '😢 프리미엄복권 꽝!' }
      } else if(type === 'mega'){
        if(rand < 0.1){ prize = 1000000; message = '🎉 메가복권 1등 대박! +1,000,000원' }
        else if(rand < 1.1){ prize = 50000; message = '🎊 메가복권 2등 당첨! +50,000원' }
        else if(rand < 11.1){ prize = 5000; message = '🎈 메가복권 3등 당첨! +5,000원' }
        else { message = '😢 메가복권 꽝!' }
      }
      
      if(prize > 0){
        gameState.money += prize
        gameState.lotteryWinnings += prize
        burstConfetti()
        checkAchievement('lotteryWinner')
      }
      
      showMessage(message, prize > 0 ? 'success' : 'fail')
      updateUI()
    }

    // 배율 게임
    function playMultiplierGame(){
      const bet = parseInt(document.getElementById('betAmount').value)
      if(gameState.money < bet){
        showMessage('베팅할 돈이 부족합니다!', 'fail')
        return
      }
      
      gameState.money -= bet
      const rand = Math.random() * 100
      let multiplier = 0, message = ''
      
      if(rand < 50){ multiplier = 2; message = '🎯 2배 당첨!' }
      else if(rand < 75){ multiplier = 3; message = '🎯 3배 당첨!' }
      else if(rand < 85){ multiplier = 5; message = '🎯 5배 당첨!' }
      else if(rand < 90){ multiplier = 10; message = '🎯 10배 대박!' }
      else { message = '😢 전액 손실!' }
      
      if(multiplier > 0){
        const winnings = bet * multiplier
        gameState.money += winnings
        gameState.gamblingWins++
        showMessage(`${message} +${winnings}원`, 'success')
        burstConfetti()
        checkAchievement('gamblingKing')
      } else {
        gameState.gamblingLoses++
        showMessage(message, 'fail')
        shakeScreen()
      }
      
      updateUI()
    }

    // 룰렛
    function spinRoulette(){
      const bet = parseInt(document.getElementById('rouletteBet').value)
      if(gameState.money < bet){
        showMessage('베팅할 돈이 부족합니다!', 'fail')
        return
      }
      
      gameState.money -= bet
      const roulette = document.getElementById('roulette')
      roulette.classList.add('spinning')
      
      setTimeout(() => {
        roulette.classList.remove('spinning')
        const colors = ['빨강', '파랑', '연두', '민트', '노랑', '보라']
        const multipliers = [1, 0.5, 1.5, 0, 3, 5]
        const result = Math.floor(Math.random() * 6)
        const winnings = bet * multipliers[result]
        
        gameState.money += winnings
        gameState.gamblingWins++
        showMessage(`🎡 ${colors[result]} 당첨! ${multipliers[result]}배! +${winnings}원`, 'success')
        burstConfetti()
        checkAchievement('gamblingKing')
        updateUI()
      }, 2000)
    }

    // 투자 시스템
    function invest(type){
      const amount = parseInt(document.getElementById(type + 'Invest').value)
      const investment = gameState.investments[type]
      
      if(gameState.money < amount){
        showMessage('투자할 돈이 부족합니다!', 'fail')
        return
      }
      
      if(investment.amount > 0){
        showMessage('이미 해당 투자가 진행중입니다!', 'fail')
        return
      }
      
      gameState.money -= amount
      investment.amount = amount
      investment.startTime = Date.now()
      
      showMessage(`${type} 투자 시작! ${amount}원`, 'success')
      updateUI()
      
      // 투자 완료 처리
      setTimeout(() => {
        const rand = Math.random()
        let result, message
        
        if(rand < investment.risk){
          // 손실
          const loss = Math.floor(investment.amount * investment.risk)
          result = investment.amount - loss
          message = `📉 ${type} 투자 손실! ${loss}원 손실`
        } else {
          // 수익
          const profit = Math.floor(investment.amount * investment.rate)
          result = investment.amount + profit
          message = `📈 ${type} 투자 성공! +${profit}원 수익`
        }
        
        gameState.money += result
        investment.amount = 0
        showMessage(message, result > investment.amount ? 'success' : 'fail')
        updateUI()
      }, investment.duration)
    }

    // 업적 시스템
    function checkAchievement(achievementKey){
      const achievement = gameState.achievements[achievementKey]
      if(!achievement || achievement.completed) return
      
      let shouldComplete = false
      
      switch(achievementKey){
        case 'firstClick': shouldComplete = true; break
        case 'promotion1': shouldComplete = gameState.level >= 1; break
        case 'millionaire': shouldComplete = gameState.money >= 1000000; break
        case 'gamblingKing': shouldComplete = gameState.gamblingWins >= 10; break
        case 'lotteryWinner': shouldComplete = gameState.lotteryWinnings >= 100000; break
        case 'ceoLevel': shouldComplete = gameState.level >= 6; break
      }
      
      if(shouldComplete){
        achievement.completed = true
        gameState.money += achievement.reward
        showMessage(`🏆 업적 달성: ${achievement.name}! +${achievement.reward}원`, 'success')
        burstConfetti()
        updateAchievements()
      }
    }

    function updateAchievements(){
      // 백만장자 업적 체크
      if(gameState.money >= 1000000) checkAchievement('millionaire')
      
      const list = document.getElementById('achievementsList')
      list.innerHTML = ''
      
      for(let [key, achievement] of Object.entries(gameState.achievements)){
        const card = document.createElement('div')
        card.className = 'card'
        card.innerHTML = `
          <h3>${achievement.completed ? '✅' : '⏳'} ${achievement.name}</h3>
          <p style="font-size:12px">${achievement.desc}</p>
          <div style="font-size:12px;color:${achievement.completed ? '#34d399' : '#fbbf24'}">
            ${achievement.completed ? '완료!' : `보상: ${achievement.reward}원`}
          </div>
        `
        list.appendChild(card)
      }
    }

    // 자동 승진
    document.getElementById('auto').addEventListener('click', () => {
      gameState.autoOn = !gameState.autoOn
      const btn = document.getElementById('auto')
      btn.textContent = gameState.autoOn ? '자동 ON' : '자동 OFF'
      btn.classList.toggle('muted')
    })

    // 승진 관련
    document.getElementById('promote').addEventListener('click', promote)
    document.getElementById('buyBoost').addEventListener('click', () => {
      const cost = calcBoostCost(gameState.level)
      if(gameState.money >= cost){
        gameState.money -= cost
        gameState.boostOwned++
        showMessage('확률 부스터 구매!', 'success')
        updateUI()
      } else {
        showMessage('돈이 부족합니다!', 'fail')
      }
    })
    document.getElementById('buyProtect').addEventListener('click', () => {
      const cost = calcProtectCost(gameState.level)
      if(gameState.money >= cost){
        gameState.money -= cost
        gameState.protectOwned++
        showMessage('강등 방지 구매!', 'success')
        updateUI()
      } else {
        showMessage('돈이 부족합니다!', 'fail')
      }
    })

    // 메시지 표시
    function showMessage(text, type){
      const msg = document.getElementById('message')
      msg.textContent = text
      msg.className = ''
      msg.style.background = type === 'success' ? 'var(--success)' : 
                           type === 'fail' ? 'var(--danger)' : 
                           type === 'warning' ? 'var(--warning)' : 'var(--accent)'
      msg.style.color = type === 'success' || type === 'fail' || type === 'warning' ? 'white' : '#04203a'
      msg.classList.add('flash')
    }

    // 시각 효과
    const canvas = document.getElementById('confettiCanvas')
    const ctx = canvas.getContext('2d')
    let W, H, confettiPieces = []
    
    function resize(){
      W = canvas.width = canvas.clientWidth
      H = canvas.height = canvas.clientHeight
    }
    window.addEventListener('resize', resize)
    resize()

    function spawnConfetti(n=60){
      for(let i=0;i<n;i++){
        confettiPieces.push({
          x: Math.random() * W,
          y: Math.random() * H - H,
          vx: Math.random() * 2 - 1,
          vy: Math.random() * 3 + 1,
          size: Math.random() * 8 + 4,
          color: `hsl(${Math.random() * 360}, 80%, 60%)`
        })
      }
    }

    function burstConfetti(){ spawnConfetti(80) }

    function animateConfetti(){
      ctx.clearRect(0, 0, W, H)
      for(let p of confettiPieces){
        p.x += p.vx
        p.y += p.vy
        ctx.fillStyle = p.color
        ctx.fillRect(p.x, p.y, p.size, p.size)
      }
      confettiPieces = confettiPieces.filter(p => p.y < H + 50)
      requestAnimationFrame(animateConfetti)
    }
    animateConfetti()

    function shakeScreen(){
      const wrap = document.querySelector('.wrap')
      wrap.classList.add('flash')
      setTimeout(() => wrap.classList.remove('flash'), 400)
    }

    // 투자 진행상황 업데이트
    function updateInvestmentProgress(){
      for(let [type, investment] of Object.entries(gameState.investments)){
        if(investment.amount > 0){
          const elapsed = Date.now() - investment.startTime
          const progress = Math.min(100, (elapsed / investment.duration) * 100)
          const progressEl = document.getElementById(type + 'Progress')
          if(progressEl) progressEl.style.width = progress + '%'
          
          const investmentEl = document.getElementById(type + 'Investment')
          if(investmentEl) investmentEl.textContent = investment.amount
        }
      }
    }

    // 게임 루프
    setInterval(() => {
      gameState.money += gameState.income
      updateUI()
      updateInvestmentProgress()
      
      // 자동 승진
      if(gameState.autoOn && gameState.level < ranks.length - 1){
        const cost = calcPromotionCost(gameState.level)
        if(gameState.money >= cost) promote()
      }
    }, 1000)

    // 초기화
    calculateIncome()
    calculateClickValue()
    updateUI()
    updateAchievements()
    </script>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        return render_template_string(ENHANCED_HTML)

    if __name__ == '__main__':
        print('Enhanced Flask 서버 실행 중: http://127.0.0.1:5000')
        app.run(debug=True)

# ------------------------
# tkinter 데스크탑 버전 (Enhanced)
# ------------------------
if RUN_TK:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import threading
    import time
    import random
    import math

    ranks = ["인턴","사원","대리","과장","부장","전무","사장","회장","명예회장","재벌총수","세계재벌왕"]
    probs = [0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.08,0.05,0.03]
    baseCost = 100
    baseIncome = 10

    # 게임 상태
    gameState = {
        'level': 0, 'money': 0, 'income': baseIncome, 'clickValue': 1,
        'boost': 0, 'protect': 0, 'autoOn': False,
        'gamblingWins': 0, 'gamblingLoses': 0, 'lotteryWinnings': 0,
        'totalClicks': 0, 'totalEarnings': 0,
        'incomeItems': {
            'coffee': {'owned': 0, 'price': 200, 'income': 5, 'multiplier': 1.15},
            'pc': {'owned': 0, 'price': 1000, 'income': 20, 'multiplier': 1.2},
            'office': {'owned': 0, 'price': 5000, 'income': 100, 'multiplier': 1.25},
            'ai': {'owned': 0, 'price': 800, 'clickBonus': 2, 'multiplier': 1.15},
            'energy': {'owned': 0, 'price': 3000, 'clickBonus': 10, 'multiplier': 1.2}
        },
        'achievements': {
            'firstClick': {'name': '첫 클릭', 'desc': '처음으로 클릭해서 돈 벌기', 'completed': False, 'reward': 100},
            'promotion1': {'name': '첫 승진', 'desc': '처음으로 승진하기', 'completed': False, 'reward': 500},
            'millionaire': {'name': '백만장자', 'desc': '100만원 모으기', 'completed': False, 'reward': 50000},
            'gamblingKing': {'name': '도박왕', 'desc': '도박에서 10번 승리', 'completed': False, 'reward': 10000},
            'clickMaster': {'name': '클릭 마스터', 'desc': '1000번 클릭하기', 'completed': False, 'reward': 5000}
        }
    }

    def calc_promo_cost(l): return int(baseCost * (2 ** l))
    def calc_boost_cost(l): return int(500 * (1.9 ** l))
    def calc_protect_cost(l): return int(1000 * (1.9 ** l))

    root = tk.Tk()
    root.title('승진 강화 게임 Enhanced (데스크탑)')
    root.geometry('800x700')
    root.configure(bg='#071024')

    # 메인 프레임
    main_frame = tk.Frame(root, bg='#071024')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # 상단 정보
    top_frame = tk.Frame(main_frame, bg='#071024')
    top_frame.pack(fill='x', pady=(0,20))

    money_label = tk.Label(top_frame, text='💰 돈: 0', font=('Helvetica',16,'bold'), fg='#34d399', bg='#071024')
    money_label.grid(row=0, column=0, padx=10, sticky='w')

    rank_label = tk.Label(top_frame, text='🏢 직급: 인턴 (0)', font=('Helvetica',16,'bold'), fg='#60a5fa', bg='#071024')
    rank_label.grid(row=0, column=1, padx=10)

    income_label = tk.Label(top_frame, text='📈 초당: 10 | 클릭당: 1', font=('Helvetica',12), fg='#e6eef8', bg='#071024')
    income_label.grid(row=1, column=0, columnspan=2, pady=(5,0))

    stats_label = tk.Label(top_frame, text='🎲 도박: 0승 0패 | 🎟️ 복권당첨: 0원', font=('Helvetica',10), fg='#9fb6d9', bg='#071024')
    stats_label.grid(row=2, column=0, columnspan=3, pady=(5,0))

    # 탭 시스템
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill='both', expand=True)

    # 메인 탭
    main_tab = tk.Frame(notebook, bg='#071024')
    notebook.add(main_tab, text='🏢 승진')

    # 클릭 영역
    click_frame = tk.Frame(main_tab, bg='#071024')
    click_frame.pack(side='left', padx=(0,20))

    click_button = tk.Button(click_frame, text='💰\n클릭!\n돈벌기', font=('Helvetica',16,'bold'), 
                            width=12, height=6, bg='#60a5fa', fg='white', 
                            command=lambda: click_money())
    click_button.pack(pady=20)

    click_info = tk.Label(click_frame, text='클릭해서 돈을 벌어보세요!', font=('Helvetica',10), 
                         fg='#9fb6d9', bg='#071024')
    click_info.pack()

    # 승진 영역
    promotion_frame = tk.Frame(main_tab, bg='#071024')
    promotion_frame.pack(side='left', fill='both', expand=True)

    promo_info = tk.Label(promotion_frame, text='승진 확률: 70% | 비용: 100', 
                         font=('Helvetica',12,'bold'), fg='#e6eef8', bg='#071024')
    promo_info.pack(pady=10)

    promo_buttons = tk.Frame(promotion_frame, bg='#071024')
    promo_buttons.pack(pady=10)

    promote_btn = tk.Button(promo_buttons, text='🚀 승진 시도', font=('Helvetica',12,'bold'),
                           bg='#34d399', fg='white', padx=20, pady=5)
    promote_btn.pack(side='left', padx=5)

    auto_btn = tk.Button(promo_buttons, text='자동 OFF', font=('Helvetica',10),
                        bg='#6b7280', fg='white', padx=15, pady=5)
    auto_btn.pack(side='left', padx=5)

    # 아이템 구매
    items_frame = tk.LabelFrame(promotion_frame, text='아이템', font=('Helvetica',10,'bold'),
                               fg='#e6eef8', bg='#071024', bd=2, relief='groove')
    items_frame.pack(fill='x', pady=10)

    boost_frame = tk.Frame(items_frame, bg='#071024')
    boost_frame.pack(fill='x', pady=5)
    tk.Label(boost_frame, text='📈 확률+10%:', font=('Helvetica',10), fg='#e6eef8', bg='#071024').pack(side='left')
    boost_buy_btn = tk.Button(boost_frame, text='구매 (500원)', bg='#fbbf24', fg='white', padx=10)
    boost_buy_btn.pack(side='right')
    boost_owned_label = tk.Label(boost_frame, text='보유: 0', font=('Helvetica',9), fg='#9fb6d9', bg='#071024')
    boost_owned_label.pack(side='right', padx=(0,10))

    protect_frame = tk.Frame(items_frame, bg='#071024')
    protect_frame.pack(fill='x', pady=5)
    tk.Label(protect_frame, text='🛡️ 강등방지:', font=('Helvetica',10), fg='#e6eef8', bg='#071024').pack(side='left')
    protect_buy_btn = tk.Button(protect_frame, text='구매 (1000원)', bg='#a855f7', fg='white', padx=10)
    protect_buy_btn.pack(side='right')
    protect_owned_label = tk.Label(protect_frame, text='보유: 0', font=('Helvetica',9), fg='#9fb6d9', bg='#071024')
    protect_owned_label.pack(side='right', padx=(0,10))

    # 수익 증대 탭
    income_tab = tk.Frame(notebook, bg='#071024')
    notebook.add(income_tab, text='💰 수익')

    income_canvas = tk.Canvas(income_tab, bg='#071024')
    income_scrollbar = ttk.Scrollbar(income_tab, orient="vertical", command=income_canvas.yview)
    income_scrollable = tk.Frame(income_canvas, bg='#071024')

    income_canvas.configure(yscrollcommand=income_scrollbar.set)
    income_canvas.pack(side="left", fill="both", expand=True)
    income_scrollbar.pack(side="right", fill="y")
    income_canvas.create_window((0, 0), window=income_scrollable, anchor="nw")

    # 도박 탭
    gambling_tab = tk.Frame(notebook, bg='#071024')
    notebook.add(gambling_tab, text='🎲 도박')

    # 복권 프레임
    lottery_frame = tk.LabelFrame(gambling_tab, text='🎟️ 복권', font=('Helvetica',12,'bold'),
                                 fg='#e6eef8', bg='#071024', bd=2, relief='groove')
    lottery_frame.pack(fill='x', pady=10, padx=10)

    lottery_buttons = tk.Frame(lottery_frame, bg='#071024')
    lottery_buttons.pack(pady=10)

    tk.Button(lottery_buttons, text='기본복권\n(50원)', bg='#fbbf24', fg='white', padx=15, pady=10,
              command=lambda: buy_lottery('basic', 50)).pack(side='left', padx=5)
    tk.Button(lottery_buttons, text='프리미엄\n(500원)', bg='#a855f7', fg='white', padx=15, pady=10,
              command=lambda: buy_lottery('premium', 500)).pack(side='left', padx=5)
    tk.Button(lottery_buttons, text='메가복권\n(2000원)', bg='#fb7185', fg='white', padx=15, pady=10,
              command=lambda: buy_lottery('mega', 2000)).pack(side='left', padx=5)

    # 배율 게임
    multiplier_frame = tk.LabelFrame(gambling_tab, text='🎯 배율 게임', font=('Helvetica',12,'bold'),
                                   fg='#e6eef8', bg='#071024', bd=2, relief='groove')
    multiplier_frame.pack(fill='x', pady=10, padx=10)

    bet_frame = tk.Frame(multiplier_frame, bg='#071024')
    bet_frame.pack(pady=10)

    tk.Label(bet_frame, text='베팅액:', font=('Helvetica',10), fg='#e6eef8', bg='#071024').pack(side='left')
    bet_entry = tk.Entry(bet_frame, width=10, font=('Helvetica',10))
    bet_entry.insert(0, '1000')
    bet_entry.pack(side='left', padx=5)

    bet_button = tk.Button(bet_frame, text='🎲 도박하기', bg='#fb7185', fg='white', padx=20, pady=5,
                          command=lambda: play_multiplier_game())
    bet_button.pack(side='left', padx=10)

    # 업적 탭
    achievement_tab = tk.Frame(notebook, bg='#071024')
    notebook.add(achievement_tab, text='🏆 업적')

    achievement_canvas = tk.Canvas(achievement_tab, bg='#071024')
    achievement_scrollbar = ttk.Scrollbar(achievement_tab, orient="vertical", command=achievement_canvas.yview)
    achievement_scrollable = tk.Frame(achievement_canvas, bg='#071024')

    achievement_canvas.configure(yscrollcommand=achievement_scrollbar.set)
    achievement_canvas.pack(side="left", fill="both", expand=True)
    achievement_scrollbar.pack(side="right", fill="y")
    achievement_canvas.create_window((0, 0), window=achievement_scrollable, anchor="nw")

    # 메시지 라벨
    message_label = tk.Label(main_frame, text='게임을 시작하세요!', font=('Helvetica',12,'bold'),
                           fg='#60a5fa', bg='#071024', pady=10)
    message_label.pack(side='bottom')

    # 함수들
    def calculate_income():
        income = baseIncome * (2 ** gameState['level'])
        for item in gameState['incomeItems'].values():
            if 'income' in item:
                income += item['income'] * item['owned']
        gameState['income'] = income

    def calculate_click_value():
        click_value = 1 + gameState['level'] // 2
        for item in gameState['incomeItems'].values():
            if 'clickBonus' in item:
                click_value += item['clickBonus'] * item['owned']
        gameState['clickValue'] = click_value

    def click_money():
        gameState['money'] += gameState['clickValue']
        gameState['totalClicks'] += 1
        gameState['totalEarnings'] += gameState['clickValue']
        
        # 첫 클릭 업적
        if not gameState['achievements']['firstClick']['completed']:
            complete_achievement('firstClick')
        
        # 클릭 마스터 업적
        if gameState['totalClicks'] >= 1000 and not gameState['achievements']['clickMaster']['completed']:
            complete_achievement('clickMaster')
        
        update_ui()

    def promote():
        if gameState['level'] >= len(ranks) - 1:
            show_message('이미 최고 직급입니다!', 'success')
            return
        
        cost = calc_promo_cost(gameState['level'])
        if gameState['money'] < cost:
            show_message('돈이 부족합니다!', 'error')
            return
        
        gameState['money'] -= cost
        chance = probs[gameState['level']]
        if gameState['boost'] > 0:
            chance += 0.10
            gameState['boost'] -= 1
        
        success = random.random() < chance
        if success:
            gameState['level'] += 1
            calculate_income()
            calculate_click_value()
            show_message(f'✅ 승진 성공! {ranks[gameState["level"]]}', 'success')
            spawn_confetti()
            
            # 첫 승진 업적
            if gameState['level'] == 1 and not gameState['achievements']['promotion1']['completed']:
                complete_achievement('promotion1')
                
        else:
            if gameState['protect'] > 0:
                gameState['protect'] -= 1
                show_message('❌ 승진 실패! (아이템으로 강등 방지)', 'warning')
            else:
                if gameState['level'] > 0:
                    gameState['level'] -= 1
                    calculate_income()
                    calculate_click_value()
                    show_message(f'❌ 승진 실패! {ranks[gameState["level"]]}로 강등', 'error')
                else:
                    show_message('❌ 승진 실패! (강등 없음)', 'error')
            shake_window()
        
        update_ui()

    def buy_income_item(item_name):
        item = gameState['incomeItems'][item_name]
        if gameState['money'] >= item['price']:
            gameState['money'] -= item['price']
            item['owned'] += 1
            item['price'] = int(item['price'] * item['multiplier'])
            calculate_income()
            calculate_click_value()
            show_message(f'{item_name} 구매 완료!', 'success')
            update_ui()
            update_income_items()
        else:
            show_message('돈이 부족합니다!', 'error')

    def buy_lottery(lottery_type, cost):
        if gameState['money'] < cost:
            show_message('돈이 부족합니다!', 'error')
            return
        
        gameState['money'] -= cost
        rand = random.random() * 100
        prize = 0
        message = ''
        
        if lottery_type == 'basic':
            if rand < 1:
                prize = 10000
                message = '🎉 기본복권 1등 당첨! +10,000원'
            elif rand < 6:
                prize = 1000
                message = '🎊 기본복권 2등 당첨! +1,000원'
            elif rand < 26:
                prize = 100
                message = '🎈 기본복권 3등 당첨! +100원'
            else:
                message = '😢 기본복권 꽝!'
        elif lottery_type == 'premium':
            if rand < 2:
                prize = 100000
                message = '🎉 프리미엄복권 1등 당첨! +100,000원'
            elif rand < 10:
                prize = 10000
                message = '🎊 프리미엄복권 2등 당첨! +10,000원'
            elif rand < 35:
                prize = 1000
                message = '🎈 프리미엄복권 3등 당첨! +1,000원'
            else:
                message = '😢 프리미엄복권 꽝!'
        elif lottery_type == 'mega':
            if rand < 0.1:
                prize = 1000000
                message = '🎉 메가복권 1등 대박! +1,000,000원'
            elif rand < 1.1:
                prize = 50000
                message = '🎊 메가복권 2등 당첨! +50,000원'
            elif rand < 11.1:
                prize = 5000
                message = '🎈 메가복권 3등 당첨! +5,000원'
            else:
                message = '😢 메가복권 꽝!'
        
        if prize > 0:
            gameState['money'] += prize
            gameState['lotteryWinnings'] += prize
            spawn_confetti()
        
        show_message(message, 'success' if prize > 0 else 'error')
        update_ui()

    def play_multiplier_game():
        try:
            bet = int(bet_entry.get())
        except ValueError:
            show_message('올바른 베팅액을 입력하세요!', 'error')
            return
        
        if gameState['money'] < bet:
            show_message('베팅할 돈이 부족합니다!', 'error')
            return
        
        gameState['money'] -= bet
        rand = random.random() * 100
        multiplier = 0
        message = ''
        
        if rand < 50:
            multiplier = 2
            message = '🎯 2배 당첨!'
        elif rand < 75:
            multiplier = 3
            message = '🎯 3배 당첨!'
        elif rand < 85:
            multiplier = 5
            message = '🎯 5배 당첨!'
        elif rand < 90:
            multiplier = 10
            message = '🎯 10배 대박!'
        else:
            message = '😢 전액 손실!'
        
        if multiplier > 0:
            winnings = bet * multiplier
            gameState['money'] += winnings
            gameState['gamblingWins'] += 1
            show_message(f'{message} +{winnings}원', 'success')
            spawn_confetti()
            
            # 도박왕 업적 체크
            if gameState['gamblingWins'] >= 10 and not gameState['achievements']['gamblingKing']['completed']:
                complete_achievement('gamblingKing')
        else:
            gameState['gamblingLoses'] += 1
            show_message(message, 'error')
            shake_window()
        
        update_ui()

    def complete_achievement(achievement_key):
        achievement = gameState['achievements'][achievement_key]
        if not achievement['completed']:
            achievement['completed'] = True
            gameState['money'] += achievement['reward']
            show_message(f'🏆 업적 달성: {achievement["name"]}! +{achievement["reward"]}원', 'success')
            spawn_confetti()
            update_achievements()

    def toggle_auto():
        gameState['autoOn'] = not gameState['autoOn']
        auto_btn.config(text='자동 ON' if gameState['autoOn'] else '자동 OFF',
                       bg='#34d399' if gameState['autoOn'] else '#6b7280')

    def buy_boost():
        cost = calc_boost_cost(gameState['level'])
        if gameState['money'] >= cost:
            gameState['money'] -= cost
            gameState['boost'] += 1
            show_message('확률 부스터 구매!', 'success')
            update_ui()
        else:
            show_message('돈이 부족합니다!', 'error')

    def buy_protect():
        cost = calc_protect_cost(gameState['level'])
        if gameState['money'] >= cost:
            gameState['money'] -= cost
            gameState['protect'] += 1
            show_message('강등 방지 구매!', 'success')
            update_ui()
        else:
            show_message('돈이 부족합니다!', 'error')

    def update_ui():
        money_label.config(text=f'💰 돈: {int(gameState["money"]):,}')
        rank_label.config(text=f'🏢 직급: {ranks[gameState["level"]]} ({gameState["level"]})')
        income_label.config(text=f'📈 초당: {gameState["income"]} | 클릭당: {gameState["clickValue"]}')
        stats_label.config(text=f'🎲 도박: {gameState["gamblingWins"]}승 {gameState["gamblingLoses"]}패 | 🎟️ 복권당첨: {int(gameState["lotteryWinnings"]):,}원')
        
        if gameState['level'] < len(ranks) - 1:
            prob = int(probs[gameState['level']] * 100)
            cost = calc_promo_cost(gameState['level'])
            promo_info.config(text=f'승진 확률: {prob}% | 비용: {cost:,}')
        else:
            promo_info.config(text='최고 직급 달성!')
        
        boost_cost = calc_boost_cost(gameState['level'])
        protect_cost = calc_protect_cost(gameState['level'])
        boost_buy_btn.config(text=f'구매 ({boost_cost:,}원)')
        protect_buy_btn.config(text=f'구매 ({protect_cost:,}원)')
        boost_owned_label.config(text=f'보유: {gameState["boost"]}')
        protect_owned_label.config(text=f'보유: {gameState["protect"]}')
        
        # 백만장자 업적 체크
        if gameState['money'] >= 1000000 and not gameState['achievements']['millionaire']['completed']:
            complete_achievement('millionaire')

    def update_income_items():
        # 기존 위젯 제거
        for widget in income_scrollable.winfo_children():
            widget.destroy()
        
        tk.Label(income_scrollable, text='💰 수익 증대 아이템', font=('Helvetica',14,'bold'),
                fg='#60a5fa', bg='#071024').pack(pady=10)
        
        items_info = [
            ('coffee', '☕ 커피머신', '초당 수익 +5'),
            ('pc', '💻 고성능 PC', '초당 수익 +20'),
            ('office', '🏠 사무실', '초당 수익 +100'),
            ('ai', '🤖 AI 어시스턴트', '클릭당 수익 +2'),
            ('energy', '⚡ 에너지 드링크', '클릭당 수익 +10')
        ]
        
        for item_key, name, desc in items_info:
            item = gameState['incomeItems'][item_key]
            frame = tk.Frame(income_scrollable, bg='#0b1220', relief='raised', bd=2)
            frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(frame, text=name, font=('Helvetica',12,'bold'),
                    fg='#e6eef8', bg='#0b1220').pack(anchor='w', padx=10, pady=(5,0))
            tk.Label(frame, text=desc, font=('Helvetica',10),
                    fg='#9fb6d9', bg='#0b1220').pack(anchor='w', padx=10)
            
            info_frame = tk.Frame(frame, bg='#0b1220')
            info_frame.pack(fill='x', padx=10, pady=(0,5))
            
            tk.Label(info_frame, text=f'가격: {item["price"]:,}원 | 보유: {item["owned"]}',
                    font=('Helvetica',10), fg='#fbbf24', bg='#0b1220').pack(side='left')
            
            buy_btn = tk.Button(info_frame, text='구매', bg='#34d399', fg='white',
                              command=lambda key=item_key: buy_income_item(key))
            buy_btn.pack(side='right')
        
        income_scrollable.update_idletasks()
        income_canvas.configure(scrollregion=income_canvas.bbox("all"))

    def update_achievements():
        # 기존 위젯 제거
        for widget in achievement_scrollable.winfo_children():
            widget.destroy()
        
        tk.Label(achievement_scrollable, text='🏆 업적 시스템', font=('Helvetica',14,'bold'),
                fg='#60a5fa', bg='#071024').pack(pady=10)
        
        for key, achievement in gameState['achievements'].items():
            frame = tk.Frame(achievement_scrollable, bg='#0b1220', relief='raised', bd=2)
            frame.pack(fill='x', padx=10, pady=5)
            
            status = '✅' if achievement['completed'] else '⏳'
            color = '#34d399' if achievement['completed'] else '#fbbf24'
            
            tk.Label(frame, text=f'{status} {achievement["name"]}', 
                    font=('Helvetica',12,'bold'), fg=color, bg='#0b1220').pack(anchor='w', padx=10, pady=(5,0))
            tk.Label(frame, text=achievement['desc'], font=('Helvetica',10),
                    fg='#9fb6d9', bg='#0b1220').pack(anchor='w', padx=10)
            
            reward_text = '완료!' if achievement['completed'] else f'보상: {achievement["reward"]}원'
            tk.Label(frame, text=reward_text, font=('Helvetica',10), fg=color, bg='#0b1220').pack(anchor='w', padx=10, pady=(0,5))
        
        achievement_scrollable.update_idletasks()
        achievement_canvas.configure(scrollregion=achievement_canvas.bbox("all"))

    def show_message(text, msg_type):
        colors = {
            'success': '#34d399',
            'error': '#fb7185',
            'warning': '#fbbf24',
            'info': '#60a5fa'
        }
        message_label.config(text=text, fg=colors.get(msg_type, '#60a5fa'))

    # 시각 효과
    confetti_particles = []

    def spawn_confetti():
        for _ in range(30):
            x = random.randint(50, 750)
            y = random.randint(50, 150)
            vx = random.uniform(-2, 2)
            vy = random.uniform(1, 4)
            color = random.choice(['#34d399', '#60a5fa', '#fbbf24', '#fb7185', '#a855f7'])
            confetti_particles.append([x, y, vx, vy, color])

    def animate_confetti():
        # 간단한 콘솔 메시지로 대체 (tkinter에서 파티클 애니메이션은 복잡)
        if confetti_particles:
            confetti_particles.clear()
            message_label.config(text='🎉 축하합니다! 🎉')
            root.after(1000, lambda: message_label.config(text=''))

    def shake_window():
        original_x = root.winfo_x()
        original_y = root.winfo_y()
        
        def shake_step(step):
            if step > 0:
                offset = 5 if step % 2 == 0 else -5
                root.geometry(f'+{original_x + offset}+{original_y}')
                root.after(50, lambda: shake_step(step - 1))
            else:
                root.geometry(f'+{original_x}+{original_y}')
        
        shake_step(6)

    # 버튼 이벤트 연결
    promote_btn.config(command=promote)
    auto_btn.config(command=toggle_auto)
    boost_buy_btn.config(command=buy_boost)
    protect_buy_btn.config(command=buy_protect)

    # 자동 수익 스레드
    def income_thread():
        while True:
            gameState['money'] += gameState['income']
            
            # 자동 승진
            if gameState['autoOn'] and gameState['level'] < len(ranks) - 1:
                cost = calc_promo_cost(gameState['level'])
                if gameState['money'] >= cost:
                    root.after(0, promote)
            
            root.after(0, update_ui)
            time.sleep(1)

    # 초기화
    calculate_income()
    calculate_click_value()
    update_ui()
    update_income_items()
    update_achievements()

    # 스레드 시작
    income_thread_obj = threading.Thread(target=income_thread, daemon=True)
    income_thread_obj.start()

    root.mainloop()