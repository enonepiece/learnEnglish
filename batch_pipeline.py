"""
Ogden 850 - 2026 現代通勤全套音訊批次生成主引擎 (Master Pipeline - 高可用韌性版)
涵蓋全套 43 集、完整 850 單字
特點：
1. 斷點續傳：自動略過已生成且大小正常 (>1MB) 的集數。
2. 網路韌性：所有網路通訊（含片頭、片尾、單字各音軌）均具備 5 次指數退避重試，自動抵抗臨時 DNS/連線逾時。
3. 說明中英文字念慢：專屬由美式母語 Jenny 以 -28% 慢速念出。
4. 英文例句慢速念兩遍：超慢 -20% + 慢速 -14% + 中文直接譯意 + 常速母語 + 3.5s Shadowing 留白。
5. 零冗餘提示詞：去除所有步驟宣告廢話。
"""

import asyncio
import json
import os
import shutil
import sys
import time
import edge_tts

# Ensure utf-8 stdout on Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ZH_VOICE = "zh-TW-HsiaoChenNeural"
EN_VOICE = "en-US-JennyNeural"

# Silence frame for 24kHz / mono / 48kbps MPEG 2 Layer III (144 bytes = 24ms)
with open("part1.mp3", "rb") as f:
    raw_data = f.read()
idx = raw_data.rfind(b"\xff\xf3\x64\xc4")
SILENT_FRAME = raw_data[idx:idx+144]

def get_silence(seconds: float) -> bytes:
    frames = int(seconds / 0.024)
    return SILENT_FRAME * frames

def load_data():
    with open("ogden_850_master.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def safe_save(text: str, voice: str, rate: str, filepath: str, max_retries: int = 5):
    """具備自動指數重試的語音合成函式，避免臨時網路震盪中斷整套生成。"""
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(filepath)
            return True
        except Exception as e:
            wait_time = 2 * (attempt + 1)
            print(f"      [TTS Retry {attempt+1}/{max_retries}] Error saving to {os.path.basename(filepath)}: {e}. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)
    raise RuntimeError(f"Failed to synthesize audio for text: '{text[:20]}...' after {max_retries} retries.")

# Define all 43 Episodes Manifest
EPISODES_MANIFEST = [
    # 模組一：Operations 操作詞 (100 詞)
    {"ep": 1, "start": 0, "end": 18, "title": "18 大核心操作動詞", "filename": "Ogden850_2026_Commute_Ep01_CoreVerbs.mp3"},
    {"ep": 2, "start": 18, "end": 38, "title": "20 空間與方向介系詞", "filename": "Ogden850_2026_Commute_Ep02_Prepositions.mp3"},
    {"ep": 3, "start": 38, "end": 60, "title": "關係詞、冠詞與代名詞篇", "filename": "Ogden850_2026_Commute_Ep03_Pronouns_Articles.mp3"},
    {"ep": 4, "start": 60, "end": 82, "title": "邏輯連接詞與空間副詞篇", "filename": "Ogden850_2026_Commute_Ep04_Connectors_Adverbs.mp3"},
    {"ep": 5, "start": 82, "end": 100, "title": "程度修飾與時空禮貌用語篇", "filename": "Ogden850_2026_Commute_Ep05_Modifiers_Directions.mp3"},

    # 模組二：General Things 通用名詞 (400 詞: index 100~499, 每集 20 詞)
    * [
        {
            "ep": 6 + i,
            "start": 100 + i * 20,
            "end": 100 + (i + 1) * 20,
            "title": f"通用概念名詞篇 ({i+1:02d}/20)",
            "filename": f"Ogden850_2026_Commute_Ep{6+i:02d}_GeneralThings_{i+1:02d}.mp3"
        }
        for i in range(20)
    ],

    # 模組三：Picturable Things 具象名詞 (200 詞: index 500~699, 每集 20 詞)
    * [
        {
            "ep": 26 + i,
            "start": 500 + i * 20,
            "end": 500 + (i + 1) * 20,
            "title": f"具象事物與生活物品篇 ({i+1:02d}/10)",
            "filename": f"Ogden850_2026_Commute_Ep{26+i:02d}_Picturable_{i+1:02d}.mp3"
        }
        for i in range(10)
    ],

    # 模組四：Qualities General 性質形容詞 (100 詞: index 700~799, 每集 20 詞)
    * [
        {
            "ep": 36 + i,
            "start": 700 + i * 20,
            "end": 700 + (i + 1) * 20,
            "title": f"基本性質與狀態形容詞篇 ({i+1:02d}/05)",
            "filename": f"Ogden850_2026_Commute_Ep{36+i:02d}_Qualities_{i+1:02d}.mp3"
        }
        for i in range(5)
    ],

    # 模組五：Qualities Opposites 成對反義詞 (50 詞: index 800~849)
    {"ep": 41, "start": 800, "end": 820, "title": "成對對比反義詞篇 (上)", "filename": "Ogden850_2026_Commute_Ep41_Opposites_01.mp3"},
    {"ep": 42, "start": 820, "end": 840, "title": "成對對比反義詞篇 (中)", "filename": "Ogden850_2026_Commute_Ep42_Opposites_02.mp3"},
    {"ep": 43, "start": 840, "end": 850, "title": "成對對比反義詞篇 (大結尾)", "filename": "Ogden850_2026_Commute_Ep43_Opposites_03.mp3"},
]

async def synthesize_word_parts(w_item, num, temp_dir):
    idx = f"{num:03d}"
    w = w_item["w"]
    zh = w_item["zh"]
    core = w_item.get("core", "")
    ex = w_item.get("ex", "")
    exz = w_item.get("exz", "")

    # 1. 中文前導序號（沉穩慢速 -5%）
    f_zh_num = os.path.join(temp_dir, f"{idx}_1_num.mp3")
    await safe_save(f"第 {num} 個詞：", ZH_VOICE, "-5%", f_zh_num)

    # 2. 說明中的單字名稱：交由美式母語 Jenny 慢速念出 (-28%)，絕不急促！
    f_en_name = os.path.join(temp_dir, f"{idx}_2_name.mp3")
    await safe_save(f"{w}.", EN_VOICE, "-28%", f_en_name)

    # 3. 中文釋義與核心意象（純淨繁體中文，沉穩慢速 -5%）
    f_zh_desc = os.path.join(temp_dir, f"{idx}_3_desc.mp3")
    zh_content = f"{zh}。{core}"
    await safe_save(zh_content, ZH_VOICE, "-5%", f_zh_desc)

    # 4. 單字發音示範第 1 遍（超慢速 -30%）
    f_w1 = os.path.join(temp_dir, f"{idx}_4_w1.mp3")
    await safe_save(f"{w}.", EN_VOICE, "-30%", f_w1)

    # 5. 單字發音示範第 2 遍（慢速 -22%）
    f_w2 = os.path.join(temp_dir, f"{idx}_5_w2.mp3")
    await safe_save(f"{w}.", EN_VOICE, "-22%", f_w2)

    # 6. 例句慢速朗讀第 1 遍（超慢分解 -20%）
    f_ex_slow1 = os.path.join(temp_dir, f"{idx}_6_ex_slow1.mp3")
    await safe_save(ex, EN_VOICE, "-20%", f_ex_slow1)

    # 7. 例句慢速朗讀第 2 遍（慢速多念一遍！-14%）
    f_ex_slow2 = os.path.join(temp_dir, f"{idx}_7_ex_slow2.mp3")
    await safe_save(ex, EN_VOICE, "-14%", f_ex_slow2)

    # 8. 例句中文翻譯（直球秒懂，慢速 -5%）
    f_trans = os.path.join(temp_dir, f"{idx}_8_trans.mp3")
    await safe_save(exz, ZH_VOICE, "-5%", f_trans)

    # 9. 例句常速母語朗讀（常速流利 +0%）
    f_ex_norm = os.path.join(temp_dir, f"{idx}_9_ex_norm.mp3")
    await safe_save(ex, EN_VOICE, "+0%", f_ex_norm)

    parts = []
    # 序號 "第 X 個詞："
    with open(f_zh_num, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.3))

    # 英文單字名稱（Jenny 慢速念出）
    with open(f_en_name, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.4))

    # 中文意象
    with open(f_zh_desc, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.6))

    # 單字教學第 1 遍（超慢 -30%）
    with open(f_w1, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.8))

    # 單字教學第 2 遍（慢速 -22%）
    with open(f_w2, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.7))

    # 例句慢速第 1 遍（超慢 -20%）
    with open(f_ex_slow1, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.8))

    # 例句慢速第 2 遍（慢速多念一遍 -14%）
    with open(f_ex_slow2, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.5))

    # 中文翻譯直給
    with open(f_trans, "rb") as f: parts.append(f.read())
    parts.append(get_silence(0.5))

    # 常速流利母語例句
    with open(f_ex_norm, "rb") as f: parts.append(f.read())
    # 影子跟讀留白
    parts.append(get_silence(3.5))

    parts.append(get_silence(0.4))
    return parts

async def generate_episode(ep_info, words_db, output_dir="audio"):
    ep_num = ep_info["ep"]
    title = ep_info["title"]
    filename = ep_info["filename"]
    target_path = os.path.join(output_dir, filename)

    # 斷點續傳：檢查檔案是否已完成
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000000:
        size_mb = os.path.getsize(target_path) / (1024 * 1024)
        print(f"[*] Ep{ep_num:02d} ({filename}) already exists ({size_mb:.2f} MB), skipping.")
        return target_path

    print(f"\n==================================================")
    print(f"[START] Starting Episode {ep_num:02d}: {title}")
    print(f"   Target: {target_path} | Words: {ep_info['start']} to {ep_info['end']}")
    print(f"==================================================")

    temp_dir = f"temp_ep_{ep_num:02d}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    audio_chunks = []

    # Intro (簡潔沉穩)
    intro_text = (
        f"歡迎收聽《Ogden 850 現代通勤英語》第 {ep_num} 單元：{title}。"
        f"請聆聽單字意象與兩次慢速例句，並在留白時間大聲跟讀。"
        f"讓我們開始。"
    )
    f_intro = os.path.join(temp_dir, "000_intro.mp3")
    await safe_save(intro_text, ZH_VOICE, "-5%", f_intro)
    with open(f_intro, "rb") as f:
        audio_chunks.append(f.read())
    audio_chunks.append(get_silence(0.8))

    # Process words
    ep_words = words_db[ep_info["start"]:ep_info["end"]]
    for i, w_item in enumerate(ep_words):
        global_num = ep_info["start"] + i + 1
        print(f"  -> [Ep{ep_num:02d}] ({i+1}/{len(ep_words)}) #{global_num} {w_item['w']}...")
        word_parts = await synthesize_word_parts(w_item, global_num, temp_dir)
        audio_chunks.extend(word_parts)

    # Outro
    outro_text = (
        f"第 {ep_num} 單元：{title} 學習完成。"
        f"建議在通勤時重複收聽複習。我們下一個單元見。"
    )
    f_outro = os.path.join(temp_dir, "999_outro.mp3")
    await safe_save(outro_text, ZH_VOICE, "-5%", f_outro)
    with open(f_outro, "rb") as f:
        audio_chunks.append(f.read())

    # Write output
    os.makedirs(output_dir, exist_ok=True)
    with open(target_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    # Clean up temp
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

    size_mb = os.path.getsize(target_path) / (1024 * 1024)
    duration_min = (os.path.getsize(target_path) / 6000) / 60
    print(f"[DONE] Finished Ep{ep_num:02d}: {filename} ({size_mb:.2f} MB, ~{duration_min:.1f} mins)")
    return target_path

async def run_pipeline(start_ep=1, end_ep=43):
    words_db = load_data()
    print(f"Loaded {len(words_db)} words. Running episodes {start_ep} to {end_ep}...")
    for ep_info in EPISODES_MANIFEST:
        if start_ep <= ep_info["ep"] <= end_ep:
            await generate_episode(ep_info, words_db)

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 43
    print(f"Starting batch runner: Episode {start} to {end}")
    asyncio.run(run_pipeline(start, end))
