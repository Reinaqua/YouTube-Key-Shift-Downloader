import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from yt_dlp import YoutubeDL
import threading
import os
import subprocess
import sys  # 新增：用於處理打包後的絕對路徑

# ================= 定義日系調色盤 =================
BG_COLOR = "#F7F5F0"     # 和紙白 (背景)
TEXT_COLOR = "#4A4A4A"   # 墨灰 (文字)
ACCENT_COLOR = "#5A83B5" # 琉璃藍 (主要按鈕與標題)
HOVER_COLOR = "#466B96"  # 深琉璃藍 (點擊與懸停)
ENTRY_BG = "#FFFFFF"     # 純白 (輸入框)

# ================= 處理打包資源路徑 =================
def resource_path(relative_path):
    """取得資源的絕對路徑，確保 PyInstaller 打包後也能找到圖示"""
    try:
        # PyInstaller 執行時會建立一個暫存資料夾 _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ================= 自定義圓角按鈕類別 =================
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=20, bg_color=ACCENT_COLOR, hover_color=HOVER_COLOR):
        super().__init__(parent, height=45, width=220, bg=BG_COLOR, highlightthickness=0, relief="flat")
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
        
        if self.is_disabled:
            color = self.disabled_bg
        elif self.is_hovered:
            color = self.hover_bg
        else:
            color = self.default_bg
            
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=color, outline="")
        self.create_arc((w-r*2, 0, w, r*2), start=0, extent=90, fill=color, outline="")
        self.create_arc((0, h-r*2, r*2, h), start=180, extent=90, fill=color, outline="")
        self.create_arc((w-r*2, h-r*2, w, h), start=270, extent=90, fill=color, outline="")
        self.create_rectangle((r, 0, w-r, h), fill=color, outline="")
        self.create_rectangle((0, r, w, h-r), fill=color, outline="")
        
        self.create_text(w/2, h/2, text=self.text, fill="white", font=("微軟正黑體", 12, "bold"))

    def on_enter(self, event):
        self.is_hovered = True
        self.draw()

    def on_leave(self, event):
        self.is_hovered = False
        self.draw()

    def on_click(self, event):
        if not self.is_disabled and self.command:
            self.command()

    def change_state(self, state, new_text=None):
        if new_text:
            self.text = new_text
        self.is_disabled = (state == tk.DISABLED)
        self.draw()

def download_video():
    url = url_entry.get()
    key_shift_str = key_cb.get()
    save_path = filedialog.askdirectory()
    
    if not url or not save_path:
        return

    download_button.change_state(tk.DISABLED, new_text="處理中...")

    def download_task():
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f"{save_path}/%(title)s.%(ext)s",
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'prefer_ffmpeg': True,
                'progress_hooks': [update_progress],
            }

            progress_label.config(text="準備中...")
            progress_bar['value'] = 0
            root.update_idletasks()

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                raw_filename = ydl.prepare_filename(info_dict)
                base_name, _ = os.path.splitext(raw_filename)
                final_mp4 = f"{base_name}.mp4"

            key_shift = int(key_shift_str)
            if key_shift != 0:
                progress_label.config(text=f"母帶級 DSP 處理中 ({key_shift:+} Key)...")
                root.update_idletasks()

                shifted_mp4 = f"{base_name}_{key_shift:+}Key.mp4"
                freq_ratio = 2 ** (key_shift / 12.0)
                
                # 修改點：加入 formants=preserve 共振峰保護，專門針對 On-Vocal 人聲
                pitch_filter = f"rubberband=pitch={freq_ratio:.7f}:transients=smooth:phase=laminar:window=long:formant=preserved"

                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-i', final_mp4,
                    '-c:v', 'copy',       
                    '-af', pitch_filter,  
                    '-c:a', 'aac', '-b:a', '320k', 
                    shifted_mp4
                ]
                
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                subprocess.run(ffmpeg_cmd, check=True, creationflags=creationflags)

                if os.path.exists(final_mp4):
                    os.remove(final_mp4)

            progress_bar['value'] = 100
            progress_label.config(text="✨ 處理完成！")
            messagebox.showinfo("完成", "影片已成功下載並處理完畢！")
            open_folder(save_path)

        except Exception as e:
            messagebox.showerror("錯誤", f"處理失敗：{e}")

        finally:
            download_button.change_state(tk.NORMAL, new_text="開始下載")

    threading.Thread(target=download_task, daemon=True).start()

def update_progress(progress):
    if progress['status'] == 'downloading':
        total_bytes = progress.get('total_bytes')
        downloaded_bytes = progress.get('downloaded_bytes', 0)
        if total_bytes:
            percentage = downloaded_bytes * 100 / total_bytes
            progress_bar['value'] = percentage
            progress_label.config(text=f"下載進度：{percentage:.2f}%")
            root.update_idletasks()
    elif progress['status'] == 'finished':
        progress_bar['value'] = 100
        progress_label.config(text="進行音軌處理中...")
        root.update_idletasks()

def open_folder(folder_path):
    try:
        if os.name == 'nt':
            os.startfile(folder_path)
        elif os.name == 'posix':
            os.system(f'open "{folder_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{folder_path}"')
    except Exception as e:
        messagebox.showerror("錯誤", f"無法開啟資料夾：{e}")

# ================= UI 介面設計 =================
root = tk.Tk()
root.title("YT 卡拉OK 下載器 (On-Vocal 專用版)")
root.geometry("520x380")
root.resizable(False, False) 
root.configure(bg=BG_COLOR)

# ================= 綁定視窗與工作列圖示 =================
try:
    icon_path = resource_path("app_icon.ico")
    root.iconbitmap(icon_path)
except Exception:
    pass 
# ==========================================================

style = ttk.Style()
style.theme_use('clam')  
style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("微軟正黑體", 11))
style.configure("TCombobox", font=("微軟正黑體", 11))
style.configure("Horizontal.TProgressbar", 
                background=ACCENT_COLOR, 
                troughcolor="#E8E4D9", 
                bordercolor=BG_COLOR, 
                lightcolor=ACCENT_COLOR, 
                darkcolor=ACCENT_COLOR)

main_frame = tk.Frame(root, bg=BG_COLOR, padx=30, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

title_label = tk.Label(main_frame, text="Karaoke Downloader", font=("微軟正黑體", 18, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
title_label.pack(pady=(0, 20))

ttk.Label(main_frame, text="YouTube 影片網址 :").pack(anchor="w")
url_entry = tk.Entry(main_frame, font=("Arial", 11), bg=ENTRY_BG, fg=TEXT_COLOR, relief="flat", highlightbackground="#D3D3D3", highlightthickness=1, highlightcolor=ACCENT_COLOR)
url_entry.pack(fill=tk.X, pady=(5, 15), ipady=5)

key_frame = tk.Frame(main_frame, bg=BG_COLOR)
key_frame.pack(fill=tk.X, pady=(0, 15))
ttk.Label(key_frame, text="選擇音高 (Key) :").pack(side=tk.LEFT)
key_options = [str(i) for i in range(-6, 7)] 
key_cb = ttk.Combobox(key_frame, values=key_options, state="readonly", width=8, font=("Arial", 11))
key_cb.set("0") 
key_cb.pack(side=tk.LEFT, padx=(10, 0))

download_button = RoundedButton(main_frame, text="開始下載", command=download_video, radius=20)
download_button.pack(pady=(10, 15))

progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode='determinate', style="Horizontal.TProgressbar")
progress_bar.pack(fill=tk.X, pady=(10, 5))

progress_label = ttk.Label(main_frame, text="等待輸入...", font=("微軟正黑體", 10))
progress_label.pack()

tk.Label(main_frame, text="※ 具備人聲共振峰保護，變調不失真", font=("微軟正黑體", 9), bg=BG_COLOR, fg="#888888").pack(pady=(5,0))

root.mainloop()