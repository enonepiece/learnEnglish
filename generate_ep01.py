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

verbs_data = [
    {
        "num": 1,
        "word": "come",
        "zh_brief": "來、到達",
        "core": "核心意象是：朝說話者或目標靠近，縮短彼此的距離。",
        "ex_en": "Can you come to the meeting online?",
        "ex_zh": "你能來參加線上會議嗎？",
        "tip": "在現代生活，come 常用於參與線上對話或新品上市。"
    },
    {
        "num": 2,
        "word": "get",
        "zh_brief": "得到、收到、變得",
        "core": "核心意象是：把東西收到手裡，或讓狀態變成新的樣子。它是萬能動詞，能代替 receive、obtain 或 become。",
        "ex_en": "Did you get my message on your phone?",
        "ex_zh": "你手機有收到我的訊息嗎？",
        "tip": "通勤與工作中極高頻：get an email、get home 都是它的延伸。"
    },
    {
        "num": 3,
        "word": "give",
        "zh_brief": "給、贈予",
        "core": "核心意象是：把自己持有的東西交出去，讓所有權或注意力轉移。",
        "ex_en": "Please give me a call when you are free.",
        "ex_zh": "你有空時請打電話給我。",
        "tip": "現代生活常說 give me a second（等我一下）或 give me a call。"
    },
    {
        "num": 4,
        "word": "go",
        "zh_brief": "去、進行",
        "core": "核心意象是：離開目前的位置，朝另一個目的地或狀態移動。",
        "ex_en": "Let's go for a walk during lunch break.",
        "ex_zh": "我們午休時間去散個步吧。",
        "tip": "也可以形容專案進行：Everything is going well。"
    },
    {
        "num": 5,
        "word": "keep",
        "zh_brief": "保持、保留",
        "core": "核心意象是：把某個東西或狀態留在手中，不讓它改變或消失。",
        "ex_en": "Keep your password safe and do not share it.",
        "ex_zh": "妥善保管你的密碼，不要透露給任何人。",
        "tip": "社群日常必備：keep in touch 保持聯繫。"
    },
    {
        "num": 6,
        "word": "let",
        "zh_brief": "讓、允許",
        "core": "核心意象是：移開障礙物，讓事情自由進行。",
        "ex_en": "Let me know if you need any help.",
        "ex_zh": "如果你需要任何幫忙，請告訴我。",
        "tip": "在現代職場中最常見的用語就是 Let me know。"
    },
    {
        "num": 7,
        "word": "make",
        "zh_brief": "做、製造、促成",
        "core": "核心意象是：動手把沒有的東西產出，或促成某個新結果。",
        "ex_en": "This new app makes our daily work much easier.",
        "ex_zh": "這款新應用程式讓我們的日常工作輕鬆許多。",
        "tip": "能替換 create 或 produce：make a plan、make a decision。"
    },
    {
        "num": 8,
        "word": "put",
        "zh_brief": "放置、安置",
        "core": "核心意象是：把物品或想法精準安放到特定位置或狀態。",
        "ex_en": "Put your phone on silent during the presentation.",
        "ex_zh": "簡報期間請將手機調成靜音。",
        "tip": "搭配介系詞威力強大：put away 收好、put off 延期。"
    },
    {
        "num": 9,
        "word": "seem",
        "zh_brief": "似乎、看起來",
        "core": "核心意象是：外觀呈現出的感受與主觀推論。",
        "ex_en": "The internet connection seems a bit slow today.",
        "ex_zh": "今天的網路連線看起來有點慢。",
        "tip": "委婉表達必備：It seems like a good idea。"
    },
    {
        "num": 10,
        "word": "take",
        "zh_brief": "拿取、花費、搭乘",
        "core": "核心意象是：主動伸手拿取、帶走、或是吸收時間與資源。",
        "ex_en": "It takes twenty minutes to commute by train.",
        "ex_zh": "搭火車通勤大約需要花二十分鐘。",
        "tip": "現代生活常用：take a photo 拍照、take a break 休息一下。"
    },
    {
        "num": 11,
        "word": "be",
        "zh_brief": "是、存在、處於",
        "core": "核心意象是：事物客觀存在，並處於某種本質或狀態。",
        "ex_en": "The new update will be available online soon.",
        "ex_zh": "最新的系統更新很快就會在線上推出。",
        "tip": "最基礎的錨定動詞，構成現在式、過去式與被動語態。"
    },
    {
        "num": 12,
        "word": "do",
        "zh_brief": "做、執行",
        "core": "核心意象是：落實實際行動，動手把任務推進完成。",
        "ex_en": "What do you do when you want to relax?",
        "ex_zh": "你想放鬆時通常都會做些什麼？",
        "tip": "與 make 不同：make 強調從無到有製作，do 強調行動與任務。"
    },
    {
        "num": 13,
        "word": "have",
        "zh_brief": "有、擁有、經歷",
        "core": "核心意象是：某件事物隨身攜帶、歸自己所有或正在體驗。",
        "ex_en": "I have several unread emails in my inbox.",
        "ex_zh": "我的收件匣裡有好幾封未讀郵件。",
        "tip": "每天祝福他人：Have a great day at work!"
    },
    {
        "num": 14,
        "word": "say",
        "zh_brief": "說、講出",
        "core": "核心意象是：把心中的想法轉化為言語表達出來。",
        "ex_en": "What did the text message say?",
        "ex_zh": "那則簡訊寫了什麼？",
        "tip": "在英文中，簡訊或路標寫了什麼也經常用 say。"
    },
    {
        "num": 15,
        "word": "see",
        "zh_brief": "看見、理解",
        "core": "核心意象是：眼睛接收光影畫面，進而大腦心領神會。",
        "ex_en": "I can see your shared screen clearly now.",
        "ex_zh": "我現在可以很清楚看到你共享的螢幕了。",
        "tip": "口語理解必備：I see what you mean，我懂你的意思了。"
    },
    {
        "num": 16,
        "word": "send",
        "zh_brief": "發送、寄出",
        "core": "核心意象是：讓物品或訊息從自身出發，投遞到目標目的地。",
        "ex_en": "Send me the link when you find it.",
        "ex_zh": "你找到連結後再傳給我。",
        "tip": "2026 年多用於傳送訊息或檔案：send a text、send a link。"
    },
    {
        "num": 17,
        "word": "may",
        "zh_brief": "可以、可能",
        "core": "核心意象是：通道沒有封閉，事情有發生的機率或被允許放行。",
        "ex_en": "You may use my charger if your battery is low.",
        "ex_zh": "如果你的手機快沒電了，可以使用我的充電器。",
        "tip": "禮貌與推測：It may take a while。"
    },
    {
        "num": 18,
        "word": "will",
        "zh_brief": "將會、願意",
        "core": "核心意象是：意志力朝未來延伸，表達堅定的承諾或即將發生的趨勢。",
        "ex_en": "I will send you a message as soon as I arrive.",
        "ex_zh": "我一到目的地就會傳訊息給你。",
        "tip": "未來式核心，同時代表主觀意志與意願。"
    }
]

async def synthesize_all():
    temp_dir = "temp_audio_clean_ep01"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    final_audio_parts = []

    print("Step 1: Generating Intro...")
    intro_zh = (
        "歡迎收聽《Ogden 850 現代通勤英語》。"
        "本系列專門為通勤者設計。在 1930 年，語言學家奧格登精選出 850 個核心單字，"
        "證明只要掌握這些詞彙，就能表達日常百分之九十的概念。"
        "而在 2026 年的今天，我們為這套經典系統注入了現代數位生活與工作情境。"
        "第一單元，我們要學習整個系統的強大心臟：18 個核心操作動詞。"
        "在每個單字中，請先聽清楚發音與核心意象，接著聆聽生活例句，並在留白時間跟著大聲朗讀。"
        "讓我們開始吧！"
    )
    intro_file = os.path.join(temp_dir, "000_intro.mp3")
    await edge_tts.Communicate(intro_zh, ZH_VOICE, rate="+5%").save(intro_file)
    with open(intro_file, "rb") as f:
        final_audio_parts.append(f.read())
    final_audio_parts.append(get_silence(1.0))

    for i, v in enumerate(verbs_data):
        print(f"Generating Verb {v['num']}: {v['word']}...")
        idx = f"{i+1:03d}"

        # 1. Chinese intro & core sense
        zh_intro = (
            f"第 {v['num']} 個核心動詞：{v['word']}。{v['zh_brief']}。"
            f"{v['core']} {v['tip']} 請聽單字發音。"
        )
        f_zh_intro = os.path.join(temp_dir, f"{idx}_1_zh.mp3")
        await edge_tts.Communicate(zh_intro, ZH_VOICE, rate="+5%").save(f_zh_intro)

        # 2. Slow word 1 (rate=-28%) - CLEAR & SLOW
        f_en_w1 = os.path.join(temp_dir, f"{idx}_2_w1.mp3")
        await edge_tts.Communicate(f"{v['word']}.", EN_VOICE, rate="-28%").save(f_en_w1)

        # 3. Slow word 2 (rate=-22%) - CLEAR & SLOW
        f_en_w2 = os.path.join(temp_dir, f"{idx}_3_w2.mp3")
        await edge_tts.Communicate(f"{v['word']}.", EN_VOICE, rate="-22%").save(f_en_w2)

        # 4. Chinese prompt for slow example
        f_zh_pre = os.path.join(temp_dir, f"{idx}_4_pre.mp3")
        await edge_tts.Communicate("請聽慢速例句：", ZH_VOICE, rate="+5%").save(f_zh_pre)

        # 5. Slow Example (rate=-12%) - PURE CLEAN ENGLISH
        f_en_slow = os.path.join(temp_dir, f"{idx}_5_ex_slow.mp3")
        await edge_tts.Communicate(v["ex_en"], EN_VOICE, rate="-12%").save(f_en_slow)

        # 6. Chinese translation of example
        zh_trans = f"例句意思是：{v['ex_zh']}。現在請聽常速例句，並跟讀。"
        f_zh_trans = os.path.join(temp_dir, f"{idx}_6_trans.mp3")
        await edge_tts.Communicate(zh_trans, ZH_VOICE, rate="+5%").save(f_zh_trans)

        # 7. Normal speed Example (rate=+0%) - PURE CLEAN ENGLISH
        f_en_norm = os.path.join(temp_dir, f"{idx}_7_ex_norm.mp3")
        await edge_tts.Communicate(v["ex_en"], EN_VOICE, rate="+0%").save(f_en_norm)

        # Assemble this word with precise pauses
        with open(f_zh_intro, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.5))

        with open(f_en_w1, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.8))  # 0.8s pause between repeated words

        with open(f_en_w2, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.6))

        with open(f_zh_pre, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.4))

        with open(f_en_slow, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.6))

        with open(f_zh_trans, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(0.5))

        with open(f_en_norm, "rb") as f:
            final_audio_parts.append(f.read())
        final_audio_parts.append(get_silence(3.5))  # 3.5s Shadowing pause for listener to repeat

        final_audio_parts.append(get_silence(0.5))

    print("Step 3: Generating Outro...")
    outro_zh = (
        "恭喜你完成了第一單元的 18 大核心動詞學習！"
        "這 18 個動詞是 Basic English 的核心引擎，只要搭配介系詞，就能替換掉數千個複雜單字。"
        "建議你在下一次通勤時重複收聽，直到例句能自然脫口而出。"
        "我們下一個單元見！"
    )
    outro_file = os.path.join(temp_dir, "999_outro.mp3")
    await edge_tts.Communicate(outro_zh, ZH_VOICE, rate="+5%").save(outro_file)
    with open(outro_file, "rb") as f:
        final_audio_parts.append(f.read())

    print("Step 4: Writing final combined MP3...")
    output_filename = "Ogden850_2026_Commute_Ep01_CoreVerbs.mp3"
    with open(output_filename, "wb") as outfile:
        for chunk in final_audio_parts:
            outfile.write(chunk)

    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    duration_min = (os.path.getsize(output_filename) / 6000) / 60
    print(f"SUCCESS! Output saved as: {output_filename}")
    print(f"File Size: {size_mb:.2f} MB | Estimated Duration: {duration_min:.1f} minutes")

if __name__ == "__main__":
    asyncio.run(synthesize_all())
