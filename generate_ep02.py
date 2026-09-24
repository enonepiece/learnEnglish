import asyncio
import os
import shutil
import edge_tts

EN_VOICE = "en-US-JennyNeural"
ZH_VOICE = "zh-TW-HsiaoChenNeural"

# Silence frame for 24kHz / mono / 48kbps MPEG 2 Layer III (144 bytes = 24ms)
with open("part1.mp3", "rb") as f:
    raw_data = f.read()
idx = raw_data.rfind(b"\xff\xf3\x64\xc4")
SILENT_FRAME = raw_data[idx:idx+144]

def get_silence(seconds: float) -> bytes:
    frames = int(seconds / 0.024)
    return SILENT_FRAME * frames

preps_data = [
    {
        "num": 19,
        "word": "about",
        "zh_brief": "關於、大約",
        "core": "核心意象是：話題圍繞著某件事打轉，或數量、距離只在附近。",
        "ex_en": "Tell me more about your new project.",
        "ex_zh": "跟我多說說關於你的新專案吧。"
    },
    {
        "num": 20,
        "word": "across",
        "zh_brief": "穿過、橫越、在對面",
        "core": "核心意象是：從這一邊橫過去，越過中間抵達另一側。",
        "ex_en": "The coffee shop is just across the street.",
        "ex_zh": "那家咖啡店就在街道的正對面。"
    },
    {
        "num": 21,
        "word": "after",
        "zh_brief": "在...之後",
        "core": "核心意象是：跟在某人某事後面，順序或時間落在後頭。",
        "ex_en": "Let's have a quick discussion after lunch.",
        "ex_zh": "我們午餐過後來做個簡短討論吧。"
    },
    {
        "num": 22,
        "word": "against",
        "zh_brief": "反對、緊靠著",
        "core": "核心意象是：迎著相反力量頂上去，或身體物品緊貼著表面支撐。",
        "ex_en": "He leaned his bicycle against the wall.",
        "ex_zh": "他把腳踏車靠在牆壁上。"
    },
    {
        "num": 23,
        "word": "among",
        "zh_brief": "在...之中、在群體中",
        "core": "核心意象是：被一群人或事物包圍，落在它們正中間。",
        "ex_en": "This app is very popular among college students.",
        "ex_zh": "這款應用程式在大學生之間非常受歡迎。"
    },
    {
        "num": 24,
        "word": "at",
        "zh_brief": "在、於",
        "core": "核心意象是：把目光精確釘在一個特定的時間點或地點座標上。",
        "ex_en": "Meet me at the station entrance at eight.",
        "ex_zh": "八點整在車站入口處跟我會合。"
    },
    {
        "num": 25,
        "word": "before",
        "zh_brief": "在...之前",
        "core": "核心意象是：排在某件事的前方，時間或位置都更早一步。",
        "ex_en": "Check your email before the morning meeting.",
        "ex_zh": "在晨會開始前先檢查一下你的電子郵件。"
    },
    {
        "num": 26,
        "word": "between",
        "zh_brief": "在...之間",
        "core": "核心意象是：落在兩個特定事物中間，被兩造夾在當中。",
        "ex_en": "The difference between these two phones is small.",
        "ex_zh": "這兩款手機之間的差異很小。"
    },
    {
        "num": 27,
        "word": "by",
        "zh_brief": "在旁、透過、在...之前",
        "core": "核心意象是：靠在身旁，或藉由某條路徑、在截止時間前完成。",
        "ex_en": "Please reply to this email by five PM.",
        "ex_zh": "請在下午五點之前回覆這封電子郵件。"
    },
    {
        "num": 28,
        "word": "down",
        "zh_brief": "向下、往低處",
        "core": "核心意象是：朝低處移動，位置順著方向或重力往下落。",
        "ex_en": "Scroll down the screen to read the full article.",
        "ex_zh": "往下滑動螢幕來閱讀完整的文章。"
    },
    {
        "num": 29,
        "word": "from",
        "zh_brief": "從、來自",
        "core": "核心意象是：離開最初的原點，帶著來源的印記往外出來。",
        "ex_en": "I work remotely from home twice a week.",
        "ex_zh": "我每週有兩天在家遠端工作。"
    },
    {
        "num": 30,
        "word": "in",
        "zh_brief": "在...裡面",
        "core": "核心意象是：被包覆在裡面，身處在邊界圍起的空間或狀態中。",
        "ex_en": "She put all her travel photos in a shared folder.",
        "ex_zh": "她把所有的旅遊照片放進了一個共享資料夾中。"
    },
    {
        "num": 31,
        "word": "off",
        "zh_brief": "脫離、關閉",
        "core": "核心意象是：從原本接觸的表面脫開、遠離或斷開電源連線。",
        "ex_en": "Remember to turn off your computer before leaving.",
        "ex_zh": "離開前記得將電腦關機。"
    },
    {
        "num": 32,
        "word": "on",
        "zh_brief": "在...上面、開啟",
        "core": "核心意象是：貼在表面之上，或是讓設備處於運作狀態。",
        "ex_en": "Click on the link to join the video call.",
        "ex_zh": "點擊連結加入視訊通話。"
    },
    {
        "num": 33,
        "word": "over",
        "zh_brief": "在上方越過、超過",
        "core": "核心意象是：在上方越過，或是數量、限度跨越了標準。",
        "ex_en": "He stayed overtime to finish the report.",
        "ex_zh": "他留下來加班以完成這份報告。"
    },
    {
        "num": 34,
        "word": "through",
        "zh_brief": "穿過、通過",
        "core": "核心意象是：從通道內部穿透過去，一頭進入、另一頭出來。",
        "ex_en": "We walked through the park on our way home.",
        "ex_zh": "我們在回家的路上穿過了公園。"
    },
    {
        "num": 35,
        "word": "to",
        "zh_brief": "到、朝向",
        "core": "核心意象是：朝向明確的目標前進，方向一直延伸到終點。",
        "ex_en": "I need to go to the post office this afternoon.",
        "ex_zh": "我今天下午需要去一趟郵局。"
    },
    {
        "num": 36,
        "word": "under",
        "zh_brief": "在...下面",
        "core": "核心意象是：壓在下方或藏在底下，被上方的遮蔽物蓋住。",
        "ex_en": "The cat likes to sleep under my desk while I work.",
        "ex_zh": "當我工作時，貓咪喜歡睡在我的書桌底下。"
    },
    {
        "num": 37,
        "word": "up",
        "zh_brief": "向上、往高處",
        "core": "核心意象是：往高處升起，位置順著方向一點點往上攀升。",
        "ex_en": "Pick up your phone and answer the call.",
        "ex_zh": "拿起你的手機接聽電話。"
    },
    {
        "num": 38,
        "word": "with",
        "zh_brief": "和...一起、伴隨",
        "core": "核心意象是：和人或物在一起，動作與狀態相互伴隨。",
        "ex_en": "I'm sharing this document with my team.",
        "ex_zh": "我正在與我的團隊共享這份文件。"
    }
]

async def synthesize_ep02():
    temp_dir = "temp_audio_clean_ep02"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    final_audio_parts = []

    print("Step 1: Generating Episode 02 Intro...")
    intro_zh = (
        "歡迎收聽《Ogden 850 現代通勤英語》第二單元：空間與方向介系詞。"
        "在奧格登的系統中，介系詞被稱為方向詞。把它們與上一單元的 18 大動詞結合，"
        "就能組裝出英語中百分之八十的動作片語。"
        "請保持專注，先聽意象解說，接著聆聽生活例句並大聲跟讀。"
        "讓我們開始吧！"
    )
    intro_file = os.path.join(temp_dir, "000_intro.mp3")
    await edge_tts.Communicate(intro_zh, ZH_VOICE, rate="+5%").save(intro_file)
    with open(intro_file, "rb") as f:
        final_audio_parts.append(f.read())
    final_audio_parts.append(get_silence(1.0))

    for i, v in enumerate(preps_data):
        print(f"Generating Preposition {v['num']}: {v['word']}...")
        idx = f"{i+1:03d}"

        # 1. Chinese intro & core sense
        zh_intro = (
            f"第 {v['num']} 個單字：{v['word']}。{v['zh_brief']}。"
            f"{v['core']} 請聽單字發音。"
        )
        f_zh_intro = os.path.join(temp_dir, f"{idx}_1_zh.mp3")
        await edge_tts.Communicate(zh_intro, ZH_VOICE, rate="+5%").save(f_zh_intro)

        # 2. Slow word 1 (rate=-28%)
        f_en_w1 = os.path.join(temp_dir, f"{idx}_2_w1.mp3")
        await edge_tts.Communicate(f"{v['word']}.", EN_VOICE, rate="-28%").save(f_en_w1)

        # 3. Slow word 2 (rate=-22%)
        f_en_w2 = os.path.join(temp_dir, f"{idx}_3_w2.mp3")
        await edge_tts.Communicate(f"{v['word']}.", EN_VOICE, rate="-22%").save(f_en_w2)

        # 4. Chinese prompt
        f_zh_pre = os.path.join(temp_dir, f"{idx}_4_pre.mp3")
        await edge_tts.Communicate("請聽慢速例句：", ZH_VOICE, rate="+5%").save(f_zh_pre)

        # 5. Slow Example (rate=-12%)
        f_en_slow = os.path.join(temp_dir, f"{idx}_5_ex_slow.mp3")
        await edge_tts.Communicate(v["ex_en"], EN_VOICE, rate="-12%").save(f_en_slow)

        # 6. Chinese translation of example
        zh_trans = f"例句意思是：{v['ex_zh']}。現在請聽常速例句，並跟讀。"
        f_zh_trans = os.path.join(temp_dir, f"{idx}_6_trans.mp3")
        await edge_tts.Communicate(zh_trans, ZH_VOICE, rate="+5%").save(f_zh_trans)

        # 7. Normal speed Example (rate=+0%)
        f_en_norm = os.path.join(temp_dir, f"{idx}_7_ex_norm.mp3")
        await edge_tts.Communicate(v["ex_en"], EN_VOICE, rate="+0%").save(f_en_norm)

        # Stitch
        with open(f_zh_intro, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.5))

        with open(f_en_w1, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.8))

        with open(f_en_w2, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.6))

        with open(f_zh_pre, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.4))

        with open(f_en_slow, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.6))

        with open(f_zh_trans, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.5))

        with open(f_en_norm, "rb") as f: final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(3.5)) # 3.5s Shadowing gap

        final_audio_parts.append(get_silence(0.5))

    print("Step 3: Generating Outro...")
    outro_zh = (
        "恭喜你完成了第二單元：20 個空間與方向介系詞的學習！"
        "當你把這 20 個介系詞與第一單元的 18 大動詞相互搭配，"
        "例如 come in、go out、put on、take off，你就能精準表達出成百上千種動作意境。"
        "建議在通勤時反覆聆聽。我們下一個單元見！"
    )
    outro_file = os.path.join(temp_dir, "999_outro.mp3")
    await edge_tts.Communicate(outro_zh, ZH_VOICE, rate="+5%").save(outro_file)
    with open(outro_file, "rb") as f:
        final_audio_parts.append(f.read())

    print("Step 4: Writing final combined MP3 for Episode 02...")
    output_filename = "Ogden850_2026_Commute_Ep02_Prepositions.mp3"
    with open(output_filename, "wb") as outfile:
        for chunk in final_audio_parts:
            outfile.write(chunk)

    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    duration_min = (os.path.getsize(output_filename) / 6000) / 60
    print(f"SUCCESS! Output saved as: {output_filename}")
    print(f"File Size: {size_mb:.2f} MB | Estimated Duration: {duration_min:.1f} minutes")

if __name__ == "__main__":
    asyncio.run(synthesize_ep02())
