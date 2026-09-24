import asyncio
import edge_tts

async def gen():
    ssml = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="en-US-JennyNeural">
Come here when you are ready.
<break time="3000ms" />
Excellent.
</voice>
</speak>"""
    # In edge_tts, communicate can take raw ssml or text. Let's test if Communicate accepts raw SSML or if there's a specific method.
    try:
        c = edge_tts.Communicate(ssml, "en-US-JennyNeural")
        await c.save("ssml_test.mp3")
        print("SSML save worked!")
    except Exception as e:
        print("Error:", e)

asyncio.run(gen())
