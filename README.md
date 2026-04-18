# YouTube 卡拉 OK 升降 Key 下載器 🎤

基於 Python 與 `yt-dlp` 開發的工具。專為需要翻唱曲目的創作者設計。利用 FFmpeg 最高級的 `rubberband` DSP 演算法，實現在下載影片的同時進行母帶級無損升降 Key。

## 🌟 核心功能
### yt downloader
* 貼上 Youtube 網址一鍵下載 1080p MP4。
* 支援 -6 到 +6 Key 調整。
* 琉璃藍極簡風 UI
* **已內建 FFmpeg ，完全免安裝環境！**
### audio replacer
* 用Ultimate Vocal Remover 分離出的純伴奏檔替換掉含有卡拉OK字幕的on vocal影片檔的音軌
* 支援 -6 到 +6 Key 調整。
* 琉璃藍極簡風 UI
## 🚀 一般使用者下載與執行方式 
請完全不要理會本頁面的程式碼！
1. 點擊頁面右側的 **[Releases]**。
2. 下載最新的 `.zip` 壓縮檔。
3. **解壓縮後，保持 `ytdownloader.exe` 、`audio_replacer.exe`與 `ffmpeg.exe` 在同一個資料夾內，直接點擊 `ytdownloader.exe` 、`audio_replacer.exe` 即可執行。**

yt downloader用於下載YT上的影片，具有升降KEY功能，貼上網址後並選好你要調整多少KEY，可以先用網頁版Transpose插件確認適合自己的KEY後下載

audio replacer提供想唱off vocal但沒有無人聲音源的卡拉OK影片的人做使用，用法為先使用yt downloader下載原key(+0)版影片後，利用Ultimate Vocal Remover將影片檔的人聲與伴奏聲分成兩個.mp3音檔，接著點開audio replacer.exe後，於影片欄位選擇原影片檔，然後聲音欄位選擇Ultimate Vocal Remover分離出來的伴奏音檔，在這裡再選擇你要的KEY，最後按下封裝即可自動將調完升降KEY的伴奏檔替換掉原影片的音檔生成off vocal版本的影片

由於`ytdownloader.exe`的升降Key功能是為on vocal設計，而`audio_replacer.exe`的升降Key功能是為off vocal設計，因此在使用yt downloader調升降Key時會對人聲進行最佳化處理而稍微劣化伴奏音頻，如果最終要變成off vocal版則先下載原key版本影片檔後用audio replacer結合時再設定升降KEY會比較合適
