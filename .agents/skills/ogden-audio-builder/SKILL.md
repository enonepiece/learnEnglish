---
name: ogden-audio-builder
description: >-
  Ogden's Basic English 850 現代通勤音訊製作與教材生成技能。
  支援依照黃金五拍教學法（慢速單字×2、核心意象解說、2026現代生活例句、常速例句、MPEG純淨靜音跟讀留白）
  自動化批次生成廣播級通勤雙語學習 MP3 與對照文字手冊。
---

# Ogden Audio Builder 技能手冊

本技能用於建置、擴充與維護基於 **Ogden's Basic English 850（奧格登 850 基礎英語）** 的現代化雙語通勤音訊課程與學習手冊。

---

## 一、 音訊架構規範：黃金 5 拍節奏

每個單字的講解音訊必須遵循以下嚴格結構，兼顧通勤無螢幕聆聽與口說肌肉記憶：

| 步驟 | 內容 | 語言/角色 | 參數與語速設定 |
| :--- | :--- | :--- | :--- |
| **第 1 拍** | 單字編號、英文、中文釋義與**核心意象（Core Sense）** | 中文導師（`zh-TW-HsiaoChenNeural`） | `rate="+5%"`，清晰俐落，重點放在「如何替換難字」 |
| **第 2 拍** | 單字發音慢速教學（第 1 次超慢 + 停頓 0.8s + 第 2 次慢速） | 英文示範（`en-US-JennyNeural`） | 第 1 次 `rate="-30%"`，第 2 次 `rate="-22%"` |
| **第 3 拍** | **慢速生活例句示範（慢速念兩遍！）** | 英文示範（`en-US-JennyNeural`） | **第 1 次 `rate="-20%"` + 停頓 0.8s + 第 2 次 `rate="-14%"`** |
| **第 4 拍** | 例句中文翻譯與日常情境用法說明 | 中文導師（`zh-TW-HsiaoChenNeural`） | `rate="+5%"` |
| **第 5 拍** | 常速生活例句 + **3.5 秒影子跟讀留白（Shadowing Gap）** | 英文示範 + MPEG 靜音幀 | 例句 `rate="+0%"`，接續拼接 3.5 秒標準 MPEG 靜音幀 |

> **⚠️ 語音合成關鍵避坑守則**：
> 1. **切勿在 `edge_tts.Communicate` 中傳入 XML/SSML 標籤**（如 `<speak>`, `<voice>`, `<break>`）。Edge-TTS 會將其 HTML 轉義成 `&lt;speak&gt;`，導致語音引擎讀出代碼雜音或例句失常。
> 2. **停頓必須使用音訊幀拼接**：MPEG 2 Layer III (24kHz / mono / 48kbps) 的靜音幀為 144 bytes（每幀 24ms）。3.5 秒靜音 = 146 幀。

---

## 二、 2026 時代語境調校原則

1. **淘汰歷史包袱詞**：
   - 降低記憶優先度：`carriage`（改學 car/train）、`plough/spade`（改學 tool）、`cork/sponge`、`apparatus`（改學 device）、`parcel`（改學 package）。
2. **融入現代高頻詞與情境**：
   - 例句必須結合 2026 現代生活：`phone, online, meeting, text/message, email, battery, screen, commute, app`。
   - 例句對比：不講 *"Send the parcel by post"*，改講 *"Send me a text when you arrive."*。

---

## 三、 全套 850 詞分輯地圖

- **模組一：Operations 操作詞（100 詞）**
  - Ep01: 18 大核心動詞（come, get, give, go, keep, let, make, put, seem, take, be, do, have, say, see, send, may, will）
  - Ep02: 20 空間與方向介系詞（about ~ with）
  - Ep03: 邏輯連接詞與核心代名詞（as, because, but, if, though, while, I, he, you, who 等）
  - Ep04: 核心疑問詞與高頻副詞（how, when, where, why, again, now, then 等）
  - Ep05: 時間、方位與禮貌詞（tomorrow, yesterday, north, south, please, yes 等）
- **模組二：General Things 通用名詞（400 詞）**：Ep06～Ep25（每集 20 詞）
- **模組三：Picturable Things 具象名詞（200 詞）**：Ep26～Ep35（每集 20 詞）
- **模組四：Qualities 性質形容詞（100 詞）**：Ep36～Ep40（每集 20 詞）
- **模組五：Opposites 成對反義詞（50 詞）**：Ep41～Ep43（成對對比錄製）
