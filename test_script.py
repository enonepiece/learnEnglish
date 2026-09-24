import asyncio
import edge_tts

async def gen():
    text = "Come here when you are ready. ... [pause] ... Good job."
    # edge-tts communicates plain text easily, or we can use break in text
    c = edge_tts.Communicate("Come here when you are ready.", "en-US-JennyNeural")
    await c.save("sample_sentence.mp3")
    print("Done")

asyncio.run(gen())
