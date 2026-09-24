import asyncio
import os
import edge_tts

EN_VOICE = "en-US-JennyNeural"
ZH_VOICE = "zh-TW-HsiaoChenNeural"

# Silence frame for 24kHz / mono / 48kbps MPEG 2 Layer III (144 bytes = 24ms)
with open("part1.mp3", "rb") as f:
    data = f.read()
idx = data.rfind(b"\xff\xf3\x64\xc4")
SILENT_FRAME = data[idx:idx+144]

def get_silence_bytes(seconds: float) -> bytes:
    frames_count = int(seconds / 0.024)
    return SILENT_FRAME * frames_count

async def test_single_word():
    # 1. Chinese Intro
    c1 = edge_tts.Communicate("第 1 個核心動詞：come。來、到達。核心意象是：朝說話者或目標靠近，縮短彼此的距離。請聽發音：", ZH_VOICE, rate="+5%")
    await c1.save("sample_1_zh.mp3")

    # 2. Slow Word 1 (rate=-28%)
    c2 = edge_tts.Communicate("come.", EN_VOICE, rate="-28%")
    await c2.save("sample_2_en_word1.mp3")

    # 3. Slow Word 2 (rate=-22%)
    c3 = edge_tts.Communicate("come.", EN_VOICE, rate="-22%")
    await c3.save("sample_3_en_word2.mp3")

    # 4. Chinese before example
    c4 = edge_tts.Communicate("請聽慢速例句：", ZH_VOICE, rate="+5%")
    await c4.save("sample_4_zh_pre.mp3")

    # 5. Slow Example (rate=-12%) - PURE CLEAN ENGLISH TEXT
    c5 = edge_tts.Communicate("Can you come to the meeting online?", EN_VOICE, rate="-12%")
    await c5.save("sample_5_en_slow.mp3")

    # 6. Chinese translation
    c6 = edge_tts.Communicate("例句意思是：你能來參加線上會議嗎？現在請聽常速例句，並跟讀。", ZH_VOICE, rate="+5%")
    await c6.save("sample_6_zh_trans.mp3")

    # 7. Normal Example (rate=+0%) - PURE CLEAN ENGLISH TEXT
    c7 = edge_tts.Communicate("Can you come to the meeting online?", EN_VOICE, rate="+0%")
    await c7.save("sample_7_en_norm.mp3")

    # 8. Assemble
    parts = [
        open("sample_1_zh.mp3", "rb").read(),
        get_silence_bytes(0.5),
        open("sample_2_en_word1.mp3", "rb").read(),
        get_silence_bytes(0.8),
        open("sample_3_en_word2.mp3", "rb").read(),
        get_silence_bytes(0.6),
        open("sample_4_zh_pre.mp3", "rb").read(),
        get_silence_bytes(0.4),
        open("sample_5_en_slow.mp3", "rb").read(),
        get_silence_bytes(0.6),
        open("sample_6_zh_trans.mp3", "rb").read(),
        get_silence_bytes(0.5),
        open("sample_7_en_norm.mp3", "rb").read(),
        get_silence_bytes(3.5), # 3.5s shadowing pause
    ]

    with open("sample_verb_come_perfect.mp3", "wb") as f:
        for p in parts:
            f.write(p)

    print("sample_verb_come_perfect.mp3 created! Size:", os.path.getsize("sample_verb_come_perfect.mp3"))

asyncio.run(test_single_word())
