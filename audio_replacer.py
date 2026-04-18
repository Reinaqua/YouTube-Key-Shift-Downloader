import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import os
import subprocess
import sys

# ================= 定義日系調色盤 (琉璃藍主題) =================
BG_COLOR = "#F7F5F0"     # 和紙白
TEXT_COLOR = "#4A4A4A"   # 墨灰
ACCENT_COLOR = "#5A83B5" # 琉璃藍
HOVER_COLOR = "#466B96"  # 深琉璃藍
ENTRY_BG = "#FFFFFF"     # 純白
BTN_BG = "#E8E4D9"       # 淺灰白

def resource_path(relative_path):
    """取得資源的絕對路徑，確保打包後能找到圖示"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ================= 自定義圓角按鈕類別 =================
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=20, bg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, width=220):
        super().__init__(parent, height=45, width=width, bg=BG_COLOR, highlightthickness=0, relief="flat")
        self.command = command
        self.radius = radius
        self.default_bg = bg_color
        self.hover_bg = hover_color
        self.disabled_bg = "#B0B0B0" 
        self.text = text
        self.is_disabled = False
        self.is_hovered = False
        
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        color = self.disabled_bg if self.is_disabled else (self.hover_bg if self.is_hovered else self.default_bg)
            
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=color, outline="")
        self.create_arc((w-r*2, 0, w, r*2), start=0, extent=90, fill=color, outline="")
        self.create_arc((0, h-r*2, r*2, h), start=180, extent=90, fill=color, outline="")
        self.create_arc((w-r*2, h-r*2, w, h), start=270, extent=90, fill=color, outline="")
        self.create_rectangle((r, 0, w-r, h), fill=color, outline="")
        self.create_rectangle((0, r, w, h-r), fill=color, outline="")
        self.create_text(w/2, h/2, text=self.text, fill="white", font=("微軟正黑體", 12, "bold"))

    def on_enter(self, event): self.is_hovered = True; self.draw()
    def on_leave(self, event): self.is_hovered = False; self.draw()
    def on_click(self, event):
        if not self.is_disabled and self.command: self.command()
    def change_state(self, state, new_text=None):
        if new_text: self.text = new_text
        self.is_disabled = (state == tk.DISABLED); self.draw()

# ================= 核心功能邏輯 =================
def select_video():
    path = filedialog.askopenfilename(title="選擇下載的影片檔案", filetypes=[("影片", "*.mp4 *.mkv *.avi")])
    if path: video_entry.delete(0, tk.END); video_entry.insert(0, path)

def select_audio():
    path = filedialog.askopenfilename(title="選擇 UVR5 伴奏檔案", filetypes=[("音訊", "*.mp3 *.wav *.flac")])
    if path: audio_entry.delete(0, tk.END); audio_entry.insert(0, path)

def start_merge():
    v_path = video_entry.get()
    a_path = audio_entry.get()
    key_shift_str = key_cb.get() # 取得選擇的 Key
    
    if not v_path or not a_path:
        messagebox.showwarning("提示", "請先選擇影片與伴奏音檔！"); return

    save_path = filedialog.asksaveasfilename(defaultextension=".mp4", initialfile="Karaoke_Final_OffVocal.mp4", filetypes=[("MP4 影片", "*.mp4")])
    if not save_path: return

    merge_button.change_state(tk.DISABLED, "處理與封裝中...")
    
    # 改變狀態文字提示
    if key_shift_str != "0":
        status_label.config(text=f"正在進行母帶級變調 ({key_shift_str} Key) 與封裝，請稍候...")
    else:
        status_label.config(text="正在進行無損替換音軌，請稍候...")

    def task():
        try:
            key_shift = int(key_shift_str)
            
            # 基礎指令：保留影片畫面，捨棄原音軌，採用新音軌
            cmd = ['ffmpeg', '-y', '-i', v_path, '-i', a_path, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy']
            
            # 如果使用者有調整 Key，則加入「純伴奏專用」的升降 Key 濾鏡 (不含 formant=preserved)
            if key_shift != 0:
                freq_ratio = 2 ** (key_shift / 12.0)
                pitch_filter = f"rubberband=pitch={freq_ratio:.7f}:transients=smooth:phase=laminar:window=long"
                cmd.extend(['-af', pitch_filter])
            
            # 結尾參數：最高音質封裝
            cmd.extend(['-c:a', 'aac', '-b:a', '320k', '-shortest', save_path])
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(cmd, check=True, creationflags=creationflags)
            
            status_label.config(text="✨ 處理完成！")
            messagebox.showinfo("完成", "影片已成功變調並封裝完畢！")
            os.startfile(os.path.dirname(save_path)) if os.name == 'nt' else None
            
        except Exception as e:
            status_label.config(text="❌ 處理失敗")
            messagebox.showerror("錯誤", f"處理失敗：{e}")
        finally:
            merge_button.change_state(tk.NORMAL, "開始變調與封裝")

    threading.Thread(target=task, daemon=True).start()

# ================= UI 佈局 =================
root = tk.Tk()
root.title("音軌替換變調封裝機")
# 修改點：把視窗高度從 380 調整到 450，以容納升降 Key 選單
root.geometry("550x450") 
root.resizable(False, False)
root.configure(bg=BG_COLOR)

try: root.iconbitmap(resource_path("app_icon.ico"))
except: pass

style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("微軟正黑體", 11))
style.configure("TButton", font=("微軟正黑體", 10))

main_frame = tk.Frame(root, bg=BG_COLOR, padx=30, pady=25)
main_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(main_frame, text="伴奏替換器", font=("微軟正黑體", 18, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0, 20))

# 影片選擇
ttk.Label(main_frame, text="1. 原始影片檔案 (0 Key) :").pack(anchor="w")
v_frame = tk.Frame(main_frame, bg=BG_COLOR)
v_frame.pack(fill=tk.X, pady=(5, 15))
video_entry = tk.Entry(v_frame, font=("Arial", 11), bg=ENTRY_BG, relief="flat", highlightbackground="#D3D3D3", highlightthickness=1)
video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
ttk.Button(v_frame, text="瀏覽", width=8, command=select_video).pack(side=tk.RIGHT, padx=(10, 0))

# 音訊選擇
ttk.Label(main_frame, text="2. UVR5 純伴奏檔案 (.mp3/.wav) :").pack(anchor="w")
a_frame = tk.Frame(main_frame, bg=BG_COLOR)
a_frame.pack(fill=tk.X, pady=(5, 15))
audio_entry = tk.Entry(a_frame, font=("Arial", 11), bg=ENTRY_BG, relief="flat", highlightbackground="#D3D3D3", highlightthickness=1)
audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
ttk.Button(a_frame, text="瀏覽", width=8, command=select_audio).pack(side=tk.RIGHT, padx=(10, 0))

# 修改點：新增選擇 Key 區塊
key_frame = tk.Frame(main_frame, bg=BG_COLOR)
key_frame.pack(fill=tk.X, pady=(5, 15))
ttk.Label(key_frame, text="3. 純伴奏升降音高 (Key) :").pack(side=tk.LEFT)
key_options = [str(i) for i in range(-6, 7)] 
key_cb = ttk.Combobox(key_frame, values=key_options, state="readonly", width=8, font=("Arial", 11))
key_cb.set("0") 
key_cb.pack(side=tk.LEFT, padx=(10, 0))

# 按鈕與狀態
merge_button = RoundedButton(main_frame, text="開始變調與封裝", command=start_merge)
merge_button.pack(pady=10)

status_label = ttk.Label(main_frame, text="等待輸入檔案...", font=("微軟正黑體", 10))
status_label.pack()

tk.Label(main_frame, text="※ 伴奏專用變調引擎 (無共振峰保護)，以防樂器失真", font=("微軟正黑體", 9), bg=BG_COLOR, fg="#888888").pack(pady=(5,0))

root.mainloop()