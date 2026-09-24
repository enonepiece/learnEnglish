"""
腳本：將完整 850 單字庫（含核心意象、2026 現代例句、中文翻譯）
依 43 集課程架構編排，生成完整版《Ogden 850 現代通勤英語》學習手冊 Markdown
"""

import json
import os

def generate_handbook():
    with open("ogden_850_master.json", "r", encoding="utf-8") as f:
        words = json.load(f)

    # 43 Episodes manifest
    manifest = [
        # 模組一：Operations (100 詞)
        {"ep": 1, "start": 0, "end": 18, "title": "18 大核心操作動詞 (The Action Engines)", "file": "Ogden850_2026_Commute_Ep01_CoreVerbs.mp3"},
        {"ep": 2, "start": 18, "end": 38, "title": "20 空間與方向介系詞 (Directional Words)", "file": "Ogden850_2026_Commute_Ep02_Prepositions.mp3"},
        {"ep": 3, "start": 38, "end": 60, "title": "關係詞、冠詞與代名詞篇 (Pronouns & Articles)", "file": "Ogden850_2026_Commute_Ep03_Pronouns_Articles.mp3"},
        {"ep": 4, "start": 60, "end": 82, "title": "邏輯連接詞與空間副詞篇 (Connectors & Adverbs)", "file": "Ogden850_2026_Commute_Ep04_Connectors_Adverbs.mp3"},
        {"ep": 5, "start": 82, "end": 100, "title": "程度修飾與時空禮貌用語篇 (Modifiers & Directions)", "file": "Ogden850_2026_Commute_Ep05_Modifiers_Directions.mp3"},

        # 模組二：General Things (400 詞)
        * [
            {
                "ep": 6 + i,
                "start": 100 + i * 20,
                "end": 100 + (i + 1) * 20,
                "title": f"通用概念名詞篇 ({i+1:02d}/20)",
                "file": f"Ogden850_2026_Commute_Ep{6+i:02d}_GeneralThings_{i+1:02d}.mp3"
            }
            for i in range(20)
        ],

        # 模組三：Picturable Things (200 詞)
        * [
            {
                "ep": 26 + i,
                "start": 500 + i * 20,
                "end": 500 + (i + 1) * 20,
                "title": f"具象事物與生活物品篇 ({i+1:02d}/10)",
                "file": f"Ogden850_2026_Commute_Ep{26+i:02d}_Picturable_{i+1:02d}.mp3"
            }
            for i in range(10)
        ],

        # 模組四：Qualities General (100 詞)
        * [
            {
                "ep": 36 + i,
                "start": 700 + i * 20,
                "end": 700 + (i + 1) * 20,
                "title": f"基本性質與狀態形容詞篇 ({i+1:02d}/05)",
                "file": f"Ogden850_2026_Commute_Ep{36+i:02d}_Qualities_{i+1:02d}.mp3"
            }
            for i in range(5)
        ],

        # 模組五：Qualities Opposites (50 詞)
        {"ep": 41, "start": 800, "end": 820, "title": "成對對比反義詞篇 (上)", "file": "Ogden850_2026_Commute_Ep41_Opposites_01.mp3"},
        {"ep": 42, "start": 820, "end": 840, "title": "成對對比反義詞篇 (中)", "file": "Ogden850_2026_Commute_Ep42_Opposites_02.mp3"},
        {"ep": 43, "start": 840, "end": 850, "title": "成對對比反義詞篇 (大結尾)", "file": "Ogden850_2026_Commute_Ep43_Opposites_03.mp3"},
    ]

    md = []
    md.append("# 《Ogden 850 現代通勤英語》全套 850 詞完整學習手冊與收聽對照講義")
    md.append("> **教材版本**：2026 現代生活增修版（全套 43 集完整收錄）  ")
    md.append("> **音訊規格**：美式母語發音（Jenny）+ 台灣專業導師解說（HsiaoChen）+ 黃金五拍慢速雙念與 3.5 秒純淨 MPEG 靜音跟讀留白  ")
    md.append("> **音訊存放路徑**：專案工作目錄之 `audio/` 資料夾\n")
    md.append("---\n")

    md.append("## 🎧 通勤學習法：黃金 5 拍節奏")
    md.append("```")
    md.append("[1. 中文意象導引] → [2. 慢速單字 × 2] → [3. 慢速生活例句] → [4. 中文情境解析] → [5. 常速例句 + 3.5秒跟讀留白]")
    md.append("```")
    md.append("- **耳聽畫面，免看螢幕**：中文導師會先解構單字的「核心意象（Core Sense）」，請在腦海中想像具體空間畫面，擺脫中文死背。")
    md.append("- **跟隨留白，大聲跟讀**：在常速例句結束後，音訊保留 **3.5 秒純淨靜音**，請在耳機中開口大聲複誦，鍛鍊發音肌肉記憶。\n")
    md.append("---\n")

    md.append("## 🗺️ 全套 43 集課程目錄與音訊進度總覽\n")
    md.append("| 集數 | 模組分類 | 單元名稱 | 涵蓋詞數 | 對應音訊檔案 | 狀態 |")
    md.append("| :---: | :--- | :--- | :---: | :--- | :---: |")

    for item in manifest:
        ep = item["ep"]
        count = item["end"] - item["start"]
        title = item["title"]
        fname = item["file"]
        status = "✅ 已生成"
        if ep <= 5:
            cat = "Operations 操作詞"
        elif ep <= 25:
            cat = "General Things 通用名詞"
        elif ep <= 35:
            cat = "Picturable Things 具象名詞"
        elif ep <= 40:
            cat = "Qualities 性質形容詞"
        else:
            cat = "Opposites 成對反義詞"
        md.append(f"| **Ep{ep:02d}** | {cat} | {title} | {count} 詞 | `{fname}` | {status} |")

    md.append("\n---\n")

    # Now write each episode in detail
    current_module = ""
    for item in manifest:
        ep = item["ep"]
        start = item["start"]
        end = item["end"]
        title = item["title"]
        fname = item["file"]

        # Module headers
        if ep == 1:
            md.append("## 🔴 模組一：Operations 操作詞篇（100 詞 / Ep01～Ep05）")
            md.append("> **本模組核心**：英語對話的動力心臟。18 個動詞搭配介系詞即可替換掉 80% 的繁複動詞！\n")
        elif ep == 6:
            md.append("## 🟢 模組二：General Things 通用概念名詞篇（400 詞 / Ep06～Ep25）")
            md.append("> **本模組核心**：涵蓋日常工作、社會運作、心理認知與物理世界的核心概念名詞。\n")
        elif ep == 26:
            md.append("## 🟡 模組三：Picturable Things 具象事物篇（200 詞 / Ep26～Ep35）")
            md.append("> **本模組核心**：能夠在腦海中精確畫出實體輪廓的生活物品、身體器官與動植物名詞。\n")
        elif ep == 36:
            md.append("## 🔵 模組四：Qualities General 基本性質形容詞篇（100 詞 / Ep36～Ep40）")
            md.append("> **本模組核心**：描述人事物狀態、外觀特徵與品質的最常用形容詞。\n")
        elif ep == 41:
            md.append("## 🟣 模組五：Qualities Opposites 成對反義形容詞篇（50 詞 / Ep41～Ep43）")
            md.append("> **本模組核心**：以二元對抗成對學習（如 clean/dirty, early/late），加深對比神經連結。\n")

        md.append(f"### 📘 Episode {ep:02d}：{title}")
        md.append(f"* **單字範圍**：#{start+1} ～ #{end}（共 {end-start} 詞）")
        md.append(f"* **音訊檔案**：[`audio/{fname}`](file:///d:/(08)_Personal/Dev/Web/learnEnglish/audio/{fname})\n")

        md.append("| # | 單字 | 中文釋義 | 核心意象 (Core Sense) | 現代生活例句 (2026 Context) | 例句中文翻譯 | 近義與代換詞 |")
        md.append("| :-: | :--- | :--- | :--- | :--- | :--- | :--- |")

        for idx in range(start, end):
            w_item = words[idx]
            num = idx + 1
            w = w_item["w"]
            zh = w_item["zh"]
            core = w_item.get("core", "").replace("\n", " ")
            ex = w_item.get("ex", "").replace("\n", " ")
            exz = w_item.get("exz", "").replace("\n", " ")
            syns = ", ".join(w_item.get("s", []))

            md.append(f"| **{num:03d}** | **{w}** | {zh} | {core} | *{ex}* | {exz} | `{syns}` |")

        md.append("\n---\n")

    # Automation guide at the bottom
    md.append("## ⚡ 自動化批次執行指南")
    md.append("本教材配套之生成引擎 `batch_pipeline.py` 支援斷點續傳與全自動生成：")
    md.append("```bash")
    md.append("# 執行全套 43 集自動化無人值守生成：")
    md.append("python batch_pipeline.py 1 43")
    md.append("```")

    full_content = "\n".join(md)
    with open("OGDEN_850_COMMUTE_HANDBOOK.md", "w", encoding="utf-8") as f:
        f.write(full_content)

    size_kb = os.path.getsize("OGDEN_850_COMMUTE_HANDBOOK.md") / 1024
    print(f"OGDEN_850_COMMUTE_HANDBOOK.md generated! Size: {size_kb:.2f} KB | Total lines: {len(md)}")

if __name__ == "__main__":
    generate_handbook()
