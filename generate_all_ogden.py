"""
Ogden 850 - 2026 現代化全套音訊批次生成腳本（純淨音訊無標籤版）
- 單字發音調慢清晰（rate="-28%" 與 rate="-22%"）
- 純淨自然英語例句（無任何 XML 標籤，美式母語標準發音）
- 精準 MPEG Silence 影子跟讀留白（Shadowing Gap 3.5 秒）
- 台灣專業親切女聲引導（zh-TW-HsiaoChenNeural）
"""
import asyncio
import json
import os
import shutil
import edge_tts

ZH_VOICE = "zh-TW-HsiaoChenNeural"
EN_VOICE = "en-US-JennyNeural"

# Read silent frame (24kHz mono 48kbps MPEG 2 Layer III)
with open("part1.mp3", "rb") as f:
    raw_data = f.read()
idx = raw_data.rfind(b"\xff\xf3\x64\xc4")
SILENT_FRAME = raw_data[idx:idx+144]

def get_silence(seconds: float) -> bytes:
    frames = int(seconds / 0.024)
    return SILENT_FRAME * frames

def load_data():
    with open("ogden_850_full.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def synthesize_category(cat_code: str, output_filename: str, title: str):
    words = [w for w in load_data() if w.get("c") == cat_code]
    print(f"Loaded {len(words)} words for category '{cat_code}' ({title})")

    temp_dir = f"temp_batch_{cat_code}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    audio_chunks = []

    # Intro
    intro_text = f"歡迎收聽《Ogden 850 現代通勤英語》：{title}。請先聽發音與核心意象，接著聆聽生活例句並跟讀。"
    f_intro = os.path.join(temp_dir, "000_intro.mp3")
    await edge_tts.Communicate(intro_text, ZH_VOICE, rate="+5%").save(f_intro)
    with open(f_intro, "rb") as f:
        audio_chunks.append(f.read())
    audio_chunks.append(get_silence(1.0))

    for i, w_item in enumerate(words):
        w = w_item["w"]
        zh = w_item["zh"]
        core = w_item.get("core", "")
        ex = w_item.get("ex", "")
        exz = w_item.get("exz", "")
        idx = f"{i+1:03d}"
        print(f"[{cat_code}] ({i+1}/{len(words)}) {w}...")

        # 1. Chinese intro
        zh_intro = f"第 {i+1} 個單字：{w}。中文釋義：{zh}。核心意象：{core}。請聽發音："
        f_zh = os.path.join(temp_dir, f"{idx}_1_zh.mp3")
        await edge_tts.Communicate(zh_intro, ZH_VOICE, rate="+5%").save(f_zh)

        # 2. Slow words
        f_w1 = os.path.join(temp_dir, f"{idx}_2_w1.mp3")
        f_w2 = os.path.join(temp_dir, f"{idx}_3_w2.mp3")
        await edge_tts.Communicate(f"{w}.", EN_VOICE, rate="-28%").save(f_w1)
        await edge_tts.Communicate(f"{w}.", EN_VOICE, rate="-22%").save(f_w2)

        # 3. Example sentences
        f_pre = os.path.join(temp_dir, f"{idx}_4_pre.mp3")
        await edge_tts.Communicate("請聽慢速例句：", ZH_VOICE, rate="+5%").save(f_pre)

        f_ex_slow = os.path.join(temp_dir, f"{idx}_5_ex_slow.mp3")
        await edge_tts.Communicate(ex, EN_VOICE, rate="-12%").save(f_ex_slow)

        f_trans = os.path.join(temp_dir, f"{idx}_6_trans.mp3")
        await edge_tts.Communicate(f"例句意思是：{exz}。現在請聽常速例句，並跟讀。", ZH_VOICE, rate="+5%").save(f_trans)

        f_ex_norm = os.path.join(temp_dir, f"{idx}_7_ex_norm.mp3")
        await edge_tts.Communicate(ex, EN_VOICE, rate="+0%").save(f_ex_norm)

        # Combine
        with open(f_zh, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(0.5))

        with open(f_w1, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(0.8))

        with open(f_w2, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(0.6))

        with open(f_pre, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(0.4))

        with open(f_ex_slow, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(0.6))

        with open(f_trans, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(0.5))

        with open(f_ex_norm, "rb") as f: audio_chunks.append(f.read())
        audio_chunks.append(get_silence(3.5)) # Shadowing gap

        audio_chunks.append(get_silence(0.5))

    # Outro
    outro_text = f"恭喜你完成了{title}的學習！請在通勤時重複複習，直到能夠自然跟讀。"
    f_outro = os.path.join(temp_dir, "999_outro.mp3")
    await edge_tts.Communicate(outro_text, ZH_VOICE, rate="+5%").save(f_outro)
    with open(f_outro, "rb") as f: audio_chunks.append(f.read())

    with open(output_filename, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    print(f"Batch completed: {output_filename} ({os.path.getsize(output_filename) / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    print("Script ready. Run with specific category.")
