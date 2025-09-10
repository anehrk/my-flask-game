"""
승진 강화 게임 - 웹(Flask) 버전 + 향상된 tkinter 데스크탑 버전
파일명: 승진게임_web_and_tk_versions.py

이 파일에는:
1) Flask 기반 웹앱(single-file) : 브라우저에서 동작하는 게임 (HTML/CSS/JS 포함)
2) tkinter 기반 데스크탑 버전 : 풍부한 이펙트와 애니메이션 포함

사용법 (웹):
- 필요: Python 3.8+
- 설치: pip install Flask
- 실행: python 승진게임_web_and_tk_versions.py --web
- 접속: http://127.0.0.1:5000

사용법 (데스크탑):
- 실행: python 승진게임_web_and_tk_versions.py --tk

참고: 웹버전은 게임 로직을 클라이언트(JS)에서 처리하므로 서버는 정적 서빙만 합니다.
아이템 비용은 직급이 높아질수록 기하급수적으로 증가하도록 조정했습니다.
"""

import sys

RUN_WEB = '--web' in sys.argv
RUN_TK = '--tk' in sys.argv

if not (RUN_WEB or RUN_TK):
    print("실행 모드를 지정하세요: --web (Flask 웹), 또는 --tk (tkinter 데스크탑)")
    print("예: python 승진게임_web_and_tk_versions.py --web")
    sys.exit(0)

# ------------------------
# Flask 웹서버 (single-file)
# ------------------------
if RUN_WEB:
    from flask import Flask, render_template_string

    app = Flask(__name__)

    INDEX_HTML = r"""
    <!doctype html>
    <html lang="ko">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>승진 강화 게임 (웹)</title>
      <style>
        :root{--bg:#0f172a;--card:#0b1220;--accent:#60a5fa;--success:#34d399;--danger:#fb7185}
        html,body{height:100%;margin:0;font-family:Inter, Roboto, Arial;background:linear-gradient(180deg,#071024 0%, #081227 100%);color:#e6eef8}
        .wrap{max-width:900px;margin:24px auto;padding:20px;border-radius:14px;background:rgba(255,255,255,0.03);box-shadow:0 8px 30px rgba(2,6,23,0.6)}
        h1{margin:0 0 8px;font-size:22px}
        .top-row{display:flex;gap:12px;align-items:center;}
        .stat{background:rgba(255,255,255,0.02);padding:12px;border-radius:10px;min-width:140px;text-align:center}
        .big{font-size:20px;font-weight:700}
        #info{margin-top:12px;height:44px;display:flex;align-items:center;justify-content:center;font-weight:600}
        .buttons{display:flex;gap:8px;margin-top:16px}
        button{padding:10px 16px;border-radius:10px;border:0;background:var(--accent);color:#04203a;font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(96,165,250,0.12)}
        button.muted{background:rgba(255,255,255,0.06);color:#cfe6ff}
        .items{display:flex;gap:8px;margin-top:12px}
        .item-card{background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;min-width:160px}
        .flash{animation:flash 0.5s linear}
        @keyframes flash{0%{transform:scale(1)}50%{transform:scale(1.04)}100%{transform:scale(1)}}
        .shake{animation:shake 0.4s}
        @keyframes shake{0%{transform:translateX(0)}25%{transform:translateX(-8px)}50%{transform:translateX(8px)}75%{transform:translateX(-6px)}100%{transform:translateX(0)}}
        .confetti-piece{position:absolute;width:8px;height:12px;border-radius:2px;opacity:0.95}
        .center{display:flex;align-items:center;justify-content:center}
        footer{margin-top:18px;color:#9fb6d9;font-size:13px;text-align:center}
      </style>
    </head>
    <body>
    <div class="wrap">
      <h1>🏢 승진 강화 게임 (웹)</h1>
      <div class="top-row">
        <div class="stat">
          <div style="font-size:12px;opacity:0.7">돈</div>
          <div id="money" class="big">0</div>
          <div style="font-size:12px;opacity:0.6">초당 수익: <span id="income">10</span></div>
        </div>
        <div class="stat">
          <div style="font-size:12px;opacity:0.7">직급</div>
          <div id="rank" class="big">인턴</div>
          <div style="font-size:12px;opacity:0.6">레벨: <span id="level">0</span></div>
        </div>
        <div style="flex:1">
          <div id="info">승진 확률: <span id="prob">70%</span> | 비용: <span id="cost">100</span></div>
          <div class="buttons">
            <button id="promote">승진 시도</button>
            <button id="auto" class="muted">자동(OFF)</button>
            <div style="flex:1"></div>
          </div>
          <div class="items">
            <div class="item-card">
              <div style="font-weight:700">확률 +10%</div>
              <div style="font-size:12px;opacity:0.7">1회용, 직급에 따라 가격 상승</div>
              <div style="margin-top:8px"><button id="buyBoost">구매</button></div>
              <div style="font-size:13px;margin-top:6px">가격: <span id="boostCost">500</span></div>
            </div>
            <div class="item-card">
              <div style="font-weight:700">강등 방지</div>
              <div style="font-size:12px;opacity:0.7">1회용, 실패해도 강등 없음</div>
              <div style="margin-top:8px"><button id="buyProtect">구매</button></div>
              <div style="font-size:13px;margin-top:6px">가격: <span id="protectCost">1000</span></div>
            </div>
            <div class="item-card">
              <div style="font-weight:700">보유 아이템</div>
              <div id="itemsOwned" style="margin-top:6px">없음</div>
            </div>
          </div>
        </div>
      </div>

      <div id="message" style="margin-top:18px;height:36px;text-align:center;font-weight:800"></div>

      <div style="height:140px;margin-top:14px;position:relative;overflow:hidden">
        <canvas id="confettiCanvas" style="position:absolute;left:0;top:0;width:100%;height:100%"></canvas>
      </div>

      <footer>웹버전: 브라우저에서 플레이하세요 — 필요하면 서버-사이드 저장(선택) 추가 가능</footer>
    </div>

    <script>
    // 게임 데이터
    const ranks = ["인턴","사원","대리","과장","부장","전무","사장","회장","명예회장","재벌총수","세계재벌왕"]
    const probs = [0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.08,0.05,0.03]
    const baseCost = 100
    const baseIncome = 10

    let level = 0
    let money = 0
    let income = baseIncome
    let boostOwned = 0
    let protectOwned = 0
    let autoOn = false

    // item costs scale with level: base * (2^level) * factor
    function calcPromotionCost(l){ return Math.floor(baseCost * Math.pow(2,l)) }
    function calcBoostCost(l){ return Math.floor(500 * Math.pow(1.9, l)) }
    function calcProtectCost(l){ return Math.floor(1000 * Math.pow(1.9, l)) }

    // DOM
    const moneyEl = document.getElementById('money')
    const incomeEl = document.getElementById('income')
    const rankEl = document.getElementById('rank')
    const levelEl = document.getElementById('level')
    const probEl = document.getElementById('prob')
    const costEl = document.getElementById('cost')
    const msg = document.getElementById('message')
    const promoteBtn = document.getElementById('promote')
    const buyBoostBtn = document.getElementById('buyBoost')
    const buyProtectBtn = document.getElementById('buyProtect')
    const itemsOwnedEl = document.getElementById('itemsOwned')
    const boostCostEl = document.getElementById('boostCost')
    const protectCostEl = document.getElementById('protectCost')
    const autoBtn = document.getElementById('auto')

    function updateUI(){
      moneyEl.textContent = money
      incomeEl.textContent = income
      rankEl.textContent = ranks[level]
      levelEl.textContent = level
      if(level < ranks.length - 1){
        probEl.textContent = Math.round(probs[level]*100) + '%'
        costEl.textContent = calcPromotionCost(level)
      } else {
        probEl.textContent = '---'
        costEl.textContent = '최고'
      }
      boostCostEl.textContent = calcBoostCost(level)
      protectCostEl.textContent = calcProtectCost(level)
      itemsOwnedEl.textContent = (boostOwned? '확률+' + boostOwned*10 + '% ':'') + (protectOwned? '강등방지 x'+protectOwned : '없음')
    }

    // income tick
    setInterval(()=>{
      money += income
      updateUI()
      if(autoOn) tryAutoPromote()
    },1000)

    function showMessage(text, cls){
      msg.textContent = text
      msg.classList.remove('flash','shake')
      void msg.offsetWidth
      if(cls === 'success') msg.classList.add('flash')
      if(cls === 'fail') msg.classList.add('shake')
    }

    function promote(){
      if(level >= ranks.length -1){ showMessage('최고 직급입니다!', 'success'); return }
      const cost = calcPromotionCost(level)
      if(money < cost){ showMessage('돈이 부족합니다!', 'fail'); return }
      money -= cost
      let chance = probs[level]
      if(boostOwned>0){ chance += 0.10; boostOwned--; }

      const succ = Math.random() < chance
      if(succ){
        level++
        income = baseIncome * Math.pow(2, level)
        showMessage('✅ 승진 성공! ' + ranks[level], 'success')
        burstConfetti()
      } else {
        if(protectOwned>0){ protectOwned--; showMessage('❌ 승진 실패! (아이템으로 강등 방지)', 'fail') }
        else {
          if(level>0) { level--; income = baseIncome * Math.pow(2, level); showMessage('❌ 승진 실패! 한 단계 강등', 'fail') }
          else showMessage('❌ 승진 실패! (강등 없음)', 'fail')
        }
        shakeScreen()
      }
      updateUI()
    }

    // auto try if money enough
    function tryAutoPromote(){
      if(level >= ranks.length -1) return
      const cost = calcPromotionCost(level)
      if(money >= cost) promote()
    }

    promoteBtn.addEventListener('click', promote)

    buyBoostBtn.addEventListener('click', ()=>{
      const c = calcBoostCost(level)
      if(money >= c){ money -= c; boostOwned++; showMessage('확률+10% 아이템 구매', 'success'); updateUI() }
      else showMessage('돈이 부족합니다', 'fail')
    })

    buyProtectBtn.addEventListener('click', ()=>{
      const c = calcProtectCost(level)
      if(money >= c){ money -= c; protectOwned++; showMessage('강등방지 아이템 구매', 'success'); updateUI() }
      else showMessage('돈이 부족합니다', 'fail')
    })

    autoBtn.addEventListener('click', ()=>{
      autoOn = !autoOn
      autoBtn.textContent = autoOn? '자동(ON)': '자동(OFF)'
      autoBtn.classList.toggle('muted')
    })

    // visual effects: confetti + shake
    const canvas = document.getElementById('confettiCanvas')
    const ctx = canvas.getContext('2d')
    let W, H, confettiPieces = []
    function resize(){ W = canvas.width = canvas.clientWidth; H = canvas.height = canvas.clientHeight }
    window.addEventListener('resize', resize)
    resize()

    function rand(min,max){ return Math.random()*(max-min)+min }
    function spawnConfetti(n=40){
      for(let i=0;i<n;i++){
        confettiPieces.push({x:rand(0,W), y:rand(-H,0), vx:rand(-0.5,0.5), vy:rand(1,4), rot:rand(0,360), vr:rand(-6,6), color:`hsl(${Math.floor(rand(0,360))},80%,60%)`, size:rand(6,12)})
      }
    }
    function burstConfetti(){ spawnConfetti(80) }

    function draw(){
      ctx.clearRect(0,0,W,H)
      for(let p of confettiPieces){
        p.x += p.vx; p.y += p.vy; p.rot += p.vr * 0.02
        ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot);
        ctx.fillStyle = p.color; ctx.fillRect(-p.size/2, -p.size/2, p.size, p.size*0.6);
        ctx.restore();
      }
      confettiPieces = confettiPieces.filter(p => p.y < H + 50)
      requestAnimationFrame(draw)
    }
    draw()

    function shakeScreen(){
      const el = document.querySelector('.wrap')
      el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake')
    }

    // 시작 UI 세팅
    updateUI()
    </script>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        return render_template_string(INDEX_HTML)

    if __name__ == '__main__':
        print('Flask 서버 실행 중: http://127.0.0.1:5000')
        app.run(debug=True)

# ------------------------
# tkinter 데스크탑 버전
# ------------------------
if RUN_TK:
    import tkinter as tk
    from tkinter import ttk
    import threading
    import time
    import random

    ranks = ["인턴","사원","대리","과장","부장","전무","사장","회장","명예회장","재벌총수","세계재벌왕"]
    probs = [0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.08,0.05,0.03]
    baseCost = 100
    baseIncome = 10

    # 상태
    state = {
      'level':0,
      'money':0,
      'income':baseIncome,
      'boost':0,
      'protect':0
    }

    def calc_promo_cost(l): return int(baseCost * (2 ** l))
    def calc_boost_cost(l): return int(500 * (1.9 ** l))
    def calc_protect_cost(l): return int(1000 * (1.9 ** l))

    root = tk.Tk()
    root.title('승진 강화 게임 (데스크탑)')
    root.geometry('640x480')
    root.configure(bg='#071024')

    style = ttk.Style()
    style.theme_use('clam')

    # UI
    top = tk.Frame(root, bg='#071024')
    top.pack(pady=12)

    money_label = tk.Label(top, text='돈: 0', font=('Helvetica',18), fg='#e6eef8', bg='#071024')
    money_label.grid(row=0,column=0,padx=12)

    rank_label = tk.Label(top, text='직급: 인턴 (0)', font=('Helvetica',18), fg='#e6eef8', bg='#071024')
    rank_label.grid(row=0,column=1,padx=12)

    income_label = tk.Label(top, text='초당: 10', font=('Helvetica',14), fg='#9fb6d9', bg='#071024')
    income_label.grid(row=0,column=2,padx=12)

    info_label = tk.Label(root, text='', font=('Helvetica',14), fg='white', bg='#071024')
    info_label.pack(pady=6)

    # 버튼 프레임
    btn_frame = tk.Frame(root, bg='#071024')
    btn_frame.pack(pady=8)

    promote_btn = tk.Button(btn_frame, text='승진 시도', font=('Helvetica',14), command=lambda: threading.Thread(target=promote_action).start())
    promote_btn.grid(row=0,column=0,padx=6)

    boost_btn = tk.Button(btn_frame, text='확률+10% 구매', command=lambda: buy_boost())
    boost_btn.grid(row=0,column=1,padx=6)

    protect_btn = tk.Button(btn_frame, text='강등방지 구매', command=lambda: buy_protect())
    protect_btn.grid(row=0,column=2,padx=6)

    items_label = tk.Label(root, text='아이템: 없음', font=('Helvetica',12), fg='#a0c4ff', bg='#071024')
    items_label.pack(pady=6)

    # 애니메이션 유틸
    def flash_label(lbl, color, times=6):
      def _flash(i):
        if i<=0:
          lbl.config(fg='#e6eef8')
        else:
          lbl.config(fg=color if i%2==0 else '#e6eef8')
          root.after(120, _flash, i-1)
      _flash(times)

    def shake_window():
      x = root.winfo_x(); y = root.winfo_y()
      for i in range(10):
        dx = (-8 if i%2==0 else 8)
        root.geometry(f'+{x+dx}+{y}')
        root.update()
        time.sleep(0.02)
      root.geometry(f'+{x}+{y}')

    # confetti canvas
    conf_canvas = tk.Canvas(root, width=600, height=140, bg='#071024', highlightthickness=0)
    conf_canvas.pack(pady=10)

    confetti = []
    def spawn_confetti(n=60):
      confetti.clear()
      for i in range(n):
        x = random.randint(0,600)
        y = random.randint(-140,0)
        vx = random.uniform(-1,1)
        vy = random.uniform(1,4)
        size = random.randint(6,12)
        color = '#' + ''.join([random.choice('89ABCDEF') for _ in range(6)])
        confetti.append([x,y,vx,vy,size,color])

    def animate_confetti():
      conf_canvas.delete('all')
      new = []
      for p in confetti:
        p[0]+=p[2]; p[1]+=p[3]
        x,y,size,color = p[0],p[1],p[4],p[5]
        conf_canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')
        if p[1] < 200:
          new.append(p)
      confetti[:] = new
      root.after(30, animate_confetti)

    animate_confetti()

    # 상태 업데이트
    def update_ui():
      money_label.config(text=f'💰 돈: {state["money"]}')
      rank_label.config(text=f'🏢 직급: {ranks[state["level"]]} ({state["level"]})')
      income_label.config(text=f'초당: {state["income"]}')
      if state['level'] < len(ranks)-1:
        info_label.config(text=f'승진 확률: {int(probs[state["level"]]*100)}% | 비용: {calc_promo_cost(state["level"]) }')
      else:
        info_label.config(text='최고 직급 달성!')
      items = ''
      if state['boost']: items += f'확률+10% x{state["boost"]} '
      if state['protect']: items += f'강등방지 x{state["protect"]}'
      items_label.config(text='아이템: ' + (items if items else '없음'))

    # 자동 소득 스레드
    def income_thread():
      while True:
        state['money'] += state['income']
        root.after(0, update_ui)
        time.sleep(1)

    threading.Thread(target=income_thread, daemon=True).start()

    # 액션: 승진
    def promote_action():
      if state['level'] >= len(ranks)-1:
        info_label.config(text='이미 최고 직급입니다!')
        flash_label(info_label, '#34d399')
        return
      cost = calc_promo_cost(state['level'])
      if state['money'] < cost:
        info_label.config(text='돈이 부족합니다!')
        flash_label(info_label, '#fb7185')
        return
      state['money'] -= cost
      chance = probs[state['level']]
      if state['boost']>0:
        chance += 0.10; state['boost'] -= 1
      success = random.random() < chance
      if success:
        state['level'] += 1
        state['income'] = int(baseIncome * (2 ** state['level']))
        info_label.config(text=f'✅ 승진 성공! {ranks[state["level"]]}')
        flash_label(info_label, '#34d399')
        spawn_confetti(80)
      else:
        if state['protect']>0:
          state['protect'] -= 1
          info_label.config(text='❌ 승진 실패! (아이템으로 강등 방지)')
          flash_label(info_label, '#60a5fa')
        else:
          if state['level']>0:
            state['level'] -= 1
            state['income'] = int(baseIncome * (2 ** state['level']))
            info_label.config(text=f'❌ 승진 실패! {ranks[state["level"]]}로 강등')
          else:
            info_label.config(text='❌ 승진 실패! (강등 없음)')
          flash_label(info_label, '#fb7185')
          threading.Thread(target=shake_window).start()
      root.after(0, update_ui)

    def buy_boost():
      c = calc_boost_cost(state['level'])
      if state['money'] >= c:
        state['money'] -= c; state['boost'] += 1; info_label.config(text='확률+10% 아이템 구매')
        flash_label(info_label, '#60a5fa')
      else:
        info_label.config(text='돈이 부족합니다')
        flash_label(info_label, '#fb7185')
      update_ui()

    def buy_protect():
      c = calc_protect_cost(state['level'])
      if state['money'] >= c:
        state['money'] -= c; state['protect'] += 1; info_label.config(text='강등방지 아이템 구매')
        flash_label(info_label, '#60a5fa')
      else:
        info_label.config(text='돈이 부족합니다')
        flash_label(info_label, '#fb7185')
      update_ui()

    promote_btn.config(command=lambda: threading.Thread(target=promote_action).start())
    boost_btn.config(command=buy_boost)
    protect_btn.config(command=buy_protect)

    update_ui()
    root.mainloop()
