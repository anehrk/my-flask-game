import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
from datetime import datetime
import subprocess
import sys

# TTS 기능 확인
TTS_AVAILABLE = False
try:
    import pyttsx3  # 발음 기능
    TTS_AVAILABLE = True
except ImportError:
    print("pyttsx3가 설치되지 않았습니다. Windows 내장 TTS를 사용합니다.")

class EnglishVocabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("영어단어 암기 프로그램")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 데이터 파일 경로
        self.data_file = "vocabulary.json"
        self.progress_file = "progress.json"
        
        # TTS 엔진 초기화
        self.tts_available = True  # Windows는 항상 TTS 사용 가능
        self.use_pyttsx3 = TTS_AVAILABLE
        
        if self.use_pyttsx3:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                voices = self.tts_engine.getProperty('voices')
                # 영어 음성 설정 (가능한 경우)
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            except:
                self.use_pyttsx3 = False
                self.tts_engine = None
        else:
            self.tts_engine = None
        
        # 데이터 초기화
        self.vocabulary = self.load_vocabulary()
        self.progress = self.load_progress()
        self.current_word_index = 0
        self.game_score = 0
        self.game_total = 0
        
        # GUI 생성
        self.create_widgets()
        
    def load_vocabulary(self):
        """단어장 데이터 로드"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 기본 단어장
        default_vocab = [
            {"word": "apple", "meaning": "사과", "pronunciation": "æpl"},
            {"word": "book", "meaning": "책", "pronunciation": "bʊk"},
            {"word": "computer", "meaning": "컴퓨터", "pronunciation": "kəmˈpjuːtər"},
            {"word": "dream", "meaning": "꿈", "pronunciation": "driːm"},
            {"word": "energy", "meaning": "에너지", "pronunciation": "ˈenərʤi"},
            {"word": "friend", "meaning": "친구", "pronunciation": "frend"},
            {"word": "guitar", "meaning": "기타", "pronunciation": "ɡɪˈtɑːr"},
            {"word": "happy", "meaning": "행복한", "pronunciation": "ˈhæpi"},
            {"word": "internet", "meaning": "인터넷", "pronunciation": "ˈɪntərnet"},
            {"word": "journey", "meaning": "여행", "pronunciation": "ˈʤɜːrni"}
        ]
        self.save_vocabulary(default_vocab)
        return default_vocab
    
    def save_vocabulary(self, vocab=None):
        """단어장 저장"""
        if vocab is None:
            vocab = self.vocabulary
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)
    
    def load_progress(self):
        """학습 진도 로드"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"learned_words": [], "scores": []}
    
    def save_progress(self):
        """학습 진도 저장"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="영어단어 암기 프로그램", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 노트북 (탭) 위젯
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 탭 생성
        self.create_study_tab()
        self.create_game_tab()
        self.create_manage_tab()
        self.create_progress_tab()
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def create_study_tab(self):
        """학습 탭 생성"""
        study_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(study_frame, text="단어 학습")
        
        # 현재 단어 표시
        self.word_label = ttk.Label(study_frame, text="", font=("Arial", 24, "bold"))
        self.word_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # 발음 표시
        self.pronunciation_label = ttk.Label(study_frame, text="", font=("Arial", 14))
        self.pronunciation_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # 뜻 표시
        self.meaning_label = ttk.Label(study_frame, text="", font=("Arial", 16))
        self.meaning_label.grid(row=2, column=0, columnspan=3, pady=20)
        
        # 버튼 프레임
        button_frame = ttk.Frame(study_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        # 버튼들
        ttk.Button(button_frame, text="이전 단어", 
                  command=self.previous_word).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="뜻 보기", 
                  command=self.show_meaning).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="발음 듣기", 
                  command=self.speak_word).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="다음 단어", 
                  command=self.next_word).grid(row=0, column=3, padx=5)
        
        # 진도 표시
        self.progress_label = ttk.Label(study_frame, text="")
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 첫 번째 단어 표시
        self.show_current_word()
    
    def create_game_tab(self):
        """게임 탭 생성"""
        game_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(game_frame, text="단어 게임")
        
        # 게임 제목
        ttk.Label(game_frame, text="영어 단어 퀴즈", 
                 font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        # 점수 표시
        self.score_label = ttk.Label(game_frame, text="점수: 0/0", font=("Arial", 14))
        self.score_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 문제 표시
        self.question_label = ttk.Label(game_frame, text="", font=("Arial", 16, "bold"))
        self.question_label.grid(row=2, column=0, columnspan=2, pady=20)
        
        # 선택지 버튼들
        self.option_buttons = []
        for i in range(4):
            btn = ttk.Button(game_frame, text="", width=30,
                           command=lambda idx=i: self.select_answer(idx))
            btn.grid(row=3+i, column=0, columnspan=2, pady=5, padx=20, sticky=(tk.W, tk.E))
            self.option_buttons.append(btn)
        
        # 게임 제어 버튼
        game_control_frame = ttk.Frame(game_frame)
        game_control_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(game_control_frame, text="게임 시작", 
                  command=self.start_game).grid(row=0, column=0, padx=5)
        ttk.Button(game_control_frame, text="다음 문제", 
                  command=self.next_question).grid(row=0, column=1, padx=5)
        
        # 결과 표시
        self.result_label = ttk.Label(game_frame, text="", font=("Arial", 12))
        self.result_label.grid(row=8, column=0, columnspan=2, pady=10)
    
    def create_manage_tab(self):
        """단어 관리 탭 생성"""
        manage_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(manage_frame, text="단어 관리")
        
        # 단어 추가 섹션
        add_frame = ttk.LabelFrame(manage_frame, text="새 단어 추가", padding="10")
        add_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(add_frame, text="영어 단어:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_word_entry = ttk.Entry(add_frame, width=20)
        self.new_word_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="뜻:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_meaning_entry = ttk.Entry(add_frame, width=20)
        self.new_meaning_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="발음:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.new_pronunciation_entry = ttk.Entry(add_frame, width=20)
        self.new_pronunciation_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(add_frame, text="단어 추가", 
                  command=self.add_word).grid(row=3, column=0, columnspan=2, pady=10)
        
        # 단어 목록
        list_frame = ttk.LabelFrame(manage_frame, text="단어 목록", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 트리뷰 (단어 목록 표시)
        columns = ("단어", "뜻", "발음")
        self.word_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.word_tree.heading(col, text=col)
            self.word_tree.column(col, width=150)
        
        self.word_tree.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.word_tree.yview)
        scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.word_tree.configure(yscrollcommand=scrollbar.set)
        
        # 삭제 버튼
        ttk.Button(list_frame, text="선택한 단어 삭제", 
                  command=self.delete_word).grid(row=1, column=0, pady=10)
        
        # 단어 목록 업데이트
        self.update_word_list()
        
        # 그리드 가중치
        manage_frame.columnconfigure(0, weight=1)
        manage_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def create_progress_tab(self):
        """진도 탭 생성"""
        progress_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(progress_frame, text="학습 진도")
        
        # 통계 표시
        stats_frame = ttk.LabelFrame(progress_frame, text="학습 통계", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 12))
        self.stats_label.grid(row=0, column=0)
        
        # 학습한 단어 목록
        learned_frame = ttk.LabelFrame(progress_frame, text="학습한 단어", padding="10")
        learned_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.learned_listbox = tk.Listbox(learned_frame, height=15)
        self.learned_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        learned_scrollbar = ttk.Scrollbar(learned_frame, orient=tk.VERTICAL, 
                                        command=self.learned_listbox.yview)
        learned_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.learned_listbox.configure(yscrollcommand=learned_scrollbar.set)
        
        # 진도 초기화 버튼
        ttk.Button(progress_frame, text="진도 초기화", 
                  command=self.reset_progress).grid(row=2, column=0, pady=10)
        
        # 진도 업데이트
        self.update_progress_display()
        
        # 그리드 가중치
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        learned_frame.columnconfigure(0, weight=1)
        learned_frame.rowconfigure(0, weight=1)
    
    def show_current_word(self):
        """현재 단어 표시"""
        if not self.vocabulary:
            return
        
        if self.current_word_index >= len(self.vocabulary):
            self.current_word_index = 0
        
        current = self.vocabulary[self.current_word_index]
        self.word_label.config(text=current["word"])
        self.pronunciation_label.config(text=f"[{current['pronunciation']}]")
        self.meaning_label.config(text="")  # 처음엔 뜻 숨김
        
        # 진도 표시
        progress_text = f"단어 {self.current_word_index + 1} / {len(self.vocabulary)}"
        self.progress_label.config(text=progress_text)
    
    def show_meaning(self):
        """뜻 보기"""
        if not self.vocabulary:
            return
        
        current = self.vocabulary[self.current_word_index]
        self.meaning_label.config(text=current["meaning"])
        
        # 학습한 단어로 기록
        word = current["word"]
        if word not in self.progress["learned_words"]:
            self.progress["learned_words"].append(word)
            self.save_progress()
            self.update_progress_display()
    
    def speak_word(self):
        """단어 발음 (고품질 음성 사용)"""
        if not self.vocabulary:
            return
        
        current = self.vocabulary[self.current_word_index]
        word = current["word"]
        
        # 방법 1: 고품질 PowerShell TTS (음성 설정 개선)
        try:
            if sys.platform.startswith('win'):
                # 더 나은 음성과 설정을 사용하는 PowerShell 스크립트
                ps_script = f"""
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                
                # 사용 가능한 음성 중에서 영어 음성 선택 (품질 우선순위)
                $voices = $synth.GetInstalledVoices() | Where-Object {{ $_.VoiceInfo.Culture.Name -match "en" }}
                
                # 우선순위: Zira > David > Mark > 기타 영어 음성
                $preferredVoices = @("Microsoft Zira Desktop", "Microsoft David Desktop", "Microsoft Mark Desktop")
                
                $selectedVoice = $null
                foreach ($preferred in $preferredVoices) {{
                    $voice = $voices | Where-Object {{ $_.VoiceInfo.Name -eq $preferred }}
                    if ($voice) {{
                        $selectedVoice = $voice.VoiceInfo.Name
                        break
                    }}
                }}
                
                if (-not $selectedVoice -and $voices) {{
                    $selectedVoice = $voices[0].VoiceInfo.Name
                }}
                
                if ($selectedVoice) {{
                    $synth.SelectVoice($selectedVoice)
                }}
                
                # 음성 품질 설정
                $synth.Rate = 0        # 보통 속도
                $synth.Volume = 100    # 최대 음량
                
                # 단어 발음
                $synth.Speak('{word}')
                """
                
                # 임시 파일에 스크립트 저장
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                    f.write(ps_script)
                    ps_file = f.name
                
                # PowerShell 실행
                result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file], 
                                     capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # 임시 파일 삭제
                os.unlink(ps_file)
                
                if result.returncode == 0:
                    return
                else:
                    print(f"PowerShell TTS 오류: {result.stderr}")
                    
        except Exception as e:
            print(f"고품질 PowerShell TTS 오류: {e}")
        
        # 방법 2: 온라인 TTS (고품질 대안들)
        self.try_online_tts(word)
    
    def try_online_tts(self, word):
        """온라인 TTS 서비스들 시도 (고품질)"""
        import webbrowser
        import urllib.parse
        
        try:
            # 선택 옵션을 사용자에게 제공
            choice = messagebox.askyesnocancel(
                "발음 선택", 
                f"'{word}' 발음을 들으시겠습니까?\n\n"
                "예: 구글 번역 (브라우저)\n"
                "아니오: 시각적 표시만\n"
                "취소: 아무것도 안 함"
            )
            
            if choice is True:
                # 구글 번역 TTS (가장 자연스러운 발음)
                encoded_word = urllib.parse.quote(word)
                url = f"https://translate.google.com/?sl=en&tl=ko&text={encoded_word}&op=translate"
                webbrowser.open(url)
                
                # 사용 안내 메시지
                messagebox.showinfo(
                    "사용 안내", 
                    "구글 번역이 열렸습니다.\n\n"
                    "1. 왼쪽 영어 단어 옆의 🔊 버튼을 클릭하세요\n"
                    "2. 더 자연스러운 발음을 들을 수 있습니다"
                )
            elif choice is False:
                # 시각적 표시
                self.show_pronunciation_popup(word, self.vocabulary[self.current_word_index]['pronunciation'])
                
        except Exception as e:
            print(f"온라인 TTS 오류: {e}")
            self.show_pronunciation_popup(word, self.vocabulary[self.current_word_index]['pronunciation'])

    
    def previous_word(self):
        """이전 단어"""
        if not self.vocabulary:
            return
        
        self.current_word_index = (self.current_word_index - 1) % len(self.vocabulary)
        self.show_current_word()
    
    def next_word(self):
        """다음 단어"""
        if not self.vocabulary:
            return
        
        self.current_word_index = (self.current_word_index + 1) % len(self.vocabulary)
        self.show_current_word()
    
    def start_game(self):
        """게임 시작"""
        if len(self.vocabulary) < 4:
            messagebox.showwarning("알림", "게임을 하려면 최소 4개의 단어가 필요합니다.")
            return
        
        self.game_score = 0
        self.game_total = 0
        self.current_question = None
        self.next_question()
    
    def next_question(self):
        """다음 문제"""
        if len(self.vocabulary) < 4:
            return
        
        # 랜덤 단어 선택
        self.current_question = random.choice(self.vocabulary)
        
        # 문제 유형 랜덤 선택 (영어->한국어 또는 한국어->영어)
        self.question_type = random.choice(["en_to_kr", "kr_to_en"])
        
        if self.question_type == "en_to_kr":
            # 영어 단어 보고 한국어 뜻 맞히기
            self.question_label.config(text=f"다음 영어 단어의 뜻은?\n'{self.current_question['word']}'")
            correct_answer = self.current_question["meaning"]
            
            # 오답 선택지 생성
            wrong_answers = [word["meaning"] for word in self.vocabulary 
                           if word["meaning"] != correct_answer]
            wrong_answers = random.sample(wrong_answers, min(3, len(wrong_answers)))
            
        else:
            # 한국어 뜻 보고 영어 단어 맞히기
            self.question_label.config(text=f"다음 뜻의 영어 단어는?\n'{self.current_question['meaning']}'")
            correct_answer = self.current_question["word"]
            
            # 오답 선택지 생성
            wrong_answers = [word["word"] for word in self.vocabulary 
                           if word["word"] != correct_answer]
            wrong_answers = random.sample(wrong_answers, min(3, len(wrong_answers)))
        
        # 선택지 섞기
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        self.correct_answer_index = options.index(correct_answer)
        
        # 버튼에 선택지 설정
        for i, option in enumerate(options):
            self.option_buttons[i].config(text=option, state='normal')
        
        # 빈 버튼 비활성화
        for i in range(len(options), 4):
            self.option_buttons[i].config(text="", state='disabled')
        
        self.result_label.config(text="")
    
    def select_answer(self, selected_index):
        """답 선택"""
        self.game_total += 1
        
        if selected_index == self.correct_answer_index:
            self.game_score += 1
            result_text = "정답! 🎉"
            result_color = "green"
        else:
            result_text = f"오답! 정답: {self.option_buttons[self.correct_answer_index]['text']}"
            result_color = "red"
        
        self.result_label.config(text=result_text, foreground=result_color)
        self.score_label.config(text=f"점수: {self.game_score}/{self.game_total}")
        
        # 점수 기록
        score_data = {
            "date": datetime.now().isoformat(),
            "score": self.game_score,
            "total": self.game_total,
            "percentage": round((self.game_score / self.game_total) * 100, 1)
        }
        self.progress["scores"].append(score_data)
        self.save_progress()
        
        # 버튼 비활성화
        for btn in self.option_buttons:
            btn.config(state='disabled')
    
    def add_word(self):
        """새 단어 추가"""
        word = self.new_word_entry.get().strip()
        meaning = self.new_meaning_entry.get().strip()
        pronunciation = self.new_pronunciation_entry.get().strip()
        
        if not word or not meaning:
            messagebox.showwarning("알림", "영어 단어와 뜻을 입력해주세요.")
            return
        
        # 중복 확인
        for existing in self.vocabulary:
            if existing["word"].lower() == word.lower():
                messagebox.showwarning("알림", "이미 존재하는 단어입니다.")
                return
        
        # 새 단어 추가
        new_word = {
            "word": word,
            "meaning": meaning,
            "pronunciation": pronunciation or word  # 발음이 없으면 단어로 대체
        }
        
        self.vocabulary.append(new_word)
        self.save_vocabulary()
        self.update_word_list()
        
        # 입력 필드 클리어
        self.new_word_entry.delete(0, tk.END)
        self.new_meaning_entry.delete(0, tk.END)
        self.new_pronunciation_entry.delete(0, tk.END)
        
        messagebox.showinfo("알림", "새 단어가 추가되었습니다.")
    
    def delete_word(self):
        """선택한 단어 삭제"""
        selected = self.word_tree.selection()
        if not selected:
            messagebox.showwarning("알림", "삭제할 단어를 선택해주세요.")
            return
        
        # 선택한 항목의 인덱스 찾기
        item = selected[0]
        item_values = self.word_tree.item(item, 'values')
        word_to_delete = item_values[0]
        
        # 확인 대화상자
        if messagebox.askyesno("확인", f"'{word_to_delete}' 단어를 삭제하시겠습니까?"):
            # 단어 삭제
            self.vocabulary = [word for word in self.vocabulary 
                             if word["word"] != word_to_delete]
            self.save_vocabulary()
            self.update_word_list()
            
            # 현재 단어 인덱스 조정
            if self.current_word_index >= len(self.vocabulary):
                self.current_word_index = 0
            
            if self.vocabulary:
                self.show_current_word()
            
            messagebox.showinfo("알림", "단어가 삭제되었습니다.")
    
    def update_word_list(self):
        """단어 목록 업데이트"""
        # 기존 항목 삭제
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 새 항목 추가
        for word_data in self.vocabulary:
            self.word_tree.insert("", tk.END, values=(
                word_data["word"],
                word_data["meaning"],
                word_data["pronunciation"]
            ))
    
    def update_progress_display(self):
        """진도 표시 업데이트"""
        total_words = len(self.vocabulary)
        learned_words = len(self.progress["learned_words"])
        
        if total_words > 0:
            percentage = round((learned_words / total_words) * 100, 1)
            stats_text = f"전체 단어: {total_words}개\n학습한 단어: {learned_words}개\n학습률: {percentage}%"
        else:
            stats_text = "등록된 단어가 없습니다."
        
        if self.progress["scores"]:
            recent_scores = self.progress["scores"][-5:]  # 최근 5개 점수
            avg_score = sum(score["percentage"] for score in recent_scores) / len(recent_scores)
            stats_text += f"\n최근 퀴즈 평균: {round(avg_score, 1)}%"
        
        self.stats_label.config(text=stats_text)
        
        # 학습한 단어 목록 업데이트
        self.learned_listbox.delete(0, tk.END)
        for word in self.progress["learned_words"]:
            self.learned_listbox.insert(tk.END, word)
    
    def reset_progress(self):
        """진도 초기화"""
        if messagebox.askyesno("확인", "학습 진도를 초기화하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            self.progress = {"learned_words": [], "scores": []}
            self.save_progress()
            self.update_progress_display()
            messagebox.showinfo("알림", "학습 진도가 초기화되었습니다.")

def main():
    root = tk.Tk()
    app = EnglishVocabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()