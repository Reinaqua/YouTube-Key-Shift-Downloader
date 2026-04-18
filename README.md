# YouTube 卡拉 OK 無損升降 Key 下載器 🎤

基於 Python 與 `yt-dlp` 開發的日系圖形化介面工具。專為需要翻唱曲目的創作者設計。利用 FFmpeg 最高級的 `rubberband` DSP 演算法，實現在下載影片的同時進行母帶級無損升降 Key。

## 🌟 核心功能
* 貼上網址即可一鍵下載 1080p MP4。
* 支援 -6 到 +6 Key 精確調整，無金屬機械音。
* 琉璃藍日系極簡風 UI，無痛上手。
* **已內建高階 FFmpeg 運算核心，完全免安裝環境！**

## 🚀 一般使用者下載與執行 (推薦)
請完全不需要理會本頁面的程式碼！
1. 點擊頁面右側的 **[Releases]**。
2. 下載最新的 `.zip` 壓縮檔。
3. **解壓縮後，保持 `ytdownloader.exe` 與 `ffmpeg.exe` 在同一個資料夾內，直接點擊 `ytdownloader.exe` 即可執行。**

## 💻 開發者源碼執行
1. 安裝依賴：`pip install -r requirements.txt`
2. 需自行準備包含 rubberband 演算法的 full build `ffmpeg.exe` 放置於根目錄。
3. 執行：`python main.py`
