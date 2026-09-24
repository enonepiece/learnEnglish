# 🎧 Ogden 850 現代通勤英語互動學院 (2026 Edition)

> 奧格登 Basic English 850 現代化通勤雙語學習系統。涵蓋全套 850 個核心單字、43 集廣播級 MP3 音訊、現代生活情境例句、核心意象解說與純淨跟讀留白。

![Version](https://img.shields.io/badge/Version-2026.1-indigo.svg)
![Status](https://img.shields.io/badge/Audio%20Episodes-43%2F43%20Done-10b981.svg)
![Words](https://img.shields.io/badge/Vocabulary-850%20Words-38bdf8.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 🌟 核心特色

1. **🎧 43 集廣播級音訊播放器**：
   - 慢速母語雙念（-30% / -22%）與 2026 現代例句。
   - 移除所有贅字提示口令，沉浸式純淨學習。
   - 例句後精確保留 **3.5 秒純淨 MPEG 靜音留白**，供通勤時進行無壓力 Shadowing 跟讀。
2. **💡 核心意象（Core Sense）圖解概念**：
   - 擺脫死背中文翻譯，以空間幾何與心理模型透徹理解每個核心詞彙的原始動力。
3. **🔍 即時全局中英文搜尋**：
   - 支援單字、中文釋義、例句關鍵字、近義替換詞即時檢索。
   - 5 大模組分類一鍵切換（操作詞、概念名詞、具象名詞、形容詞、反義詞）。
4. **📺 YouTube 16:9 錄播展示模式**：
   - 內建 1080p 比例全螢幕字卡，包含 3.5 秒跟讀倒數條，可直接用於螢幕錄製產出 YouTube 英語教學短影音。
5. **🌓 質感深色 / 淺色主題**：
   - 現代深太空（Deep Space）高對比深色介面，夜間通勤使用不刺眼。

---

## 🗺️ 課程架構總覽 (43 Episodes)

| 模組分類 | 集數範圍 | 詞數 | 核心焦點 |
| :--- | :---: | :---: | :--- |
| **Operations 操作詞** | Ep01 ～ Ep05 | 100 詞 | 英語動力的心臟！18 大操作動詞與方向介系詞搭配。 |
| **General Things 通用名詞** | Ep06 ～ Ep25 | 400 詞 | 抽象概念、邏輯思考、時間空間與社會生活必備詞彙。 |
| **Picturable Things 具象名詞** | Ep26 ～ Ep35 | 200 詞 | 具體生活物品、人體部位、自然世界與現代科技實體。 |
| **Qualities 基本形容詞** | Ep36 ～ Ep40 | 100 詞 | 描述狀態、性質與程度的基礎修飾語。 |
| **Opposites 成對反義詞** | Ep41 ～ Ep43 | 50 詞 | 高頻對稱反義詞，透過兩極對比深化大腦記憶。 |

---

## 🚀 部署至 GitHub Pages 教學

本專案採用純靜態架構（HTML5 + Vanilla CSS + ES6 JavaScript），**無需任何 build 或編譯步驟**，直接推送到 GitHub 即可啟動：

### 步驟 1：在 GitHub 建立新儲存庫
前往 [GitHub.com](https://github.com/new) 建立一個新的 Public 儲存庫（例如 `ogden850-commute-english`）。

### 步驟 2：初始化本機 Git 並推送
在專案目錄下開啟終端機（PowerShell / CMD），執行：

```bash
# 1. 初始化 Git
git init

# 2. 加入所有檔案並提交
git add .
git commit -m "feat: initial commit with 43 episodes audio and interactive handbook"

# 3. 綁定 GitHub 遠端倉庫（請替換為您的倉庫網址）
git remote add origin https://github.com/您的帳號/ogden850-commute-english.git

# 4. 推送到 main 分支
git branch -M main
git push -u origin main
```

### 步驟 3：開啟 GitHub Pages
1. 進入您 GitHub 倉庫的 **Settings**（設定）頁面。
2. 點選左側選單的 **Pages**。
3. 在 **Build and deployment** 下方的 **Branch** 選擇 `main`，資料夾選擇 `/(root)`。
4. 點擊 **Save**。
5. 等待約 1~2 分鐘，上方即會出現您的專屬線上網址：  
   `https://您的帳號.github.io/ogden850-commute-english/`

---

## 💻 本地端預覽

直接以瀏覽器雙擊打開 `index.html` 即可使用；或使用輕量本地伺服器：

```bash
# 使用 Python 內建伺服器預覽
python -m http.server 8000
```
開啟瀏覽器前往 `http://localhost:8000` 即可享有完整體驗。

---

## 📄 專案目錄結構

```
.
├── audio/                          # 43 集完整 MP3 音訊檔案
├── index.html                      # 互動學習網頁主入口 (GitHub Pages)
├── styles.css                      # 現代質感設計系統與深淺色主題
├── app.js                          # 播放器邏輯、搜尋、TTS與展示模式
├── data.js                         # 850 詞與 43 集課程清單資料
├── ogden_850_master.json           # 850 詞結構化核心資料庫
├── OGDEN_850_COMMUTE_HANDBOOK.md   # 完整版 Markdown 學習手冊
├── .nojekyll                       # 告知 GitHub Pages 繞過 Jekyll 處理
└── README.md                       # 專案說明與部署指南
```
