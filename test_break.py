import asyncio
import os
import edge_tts.communicate

orig_escape = edge_tts.communicate.escape

def custom_escape(data, entities={}):
    if "<break" in data:
        return data
    return orig_escape(data, entities)

edge_tts.communicate.escape = custom_escape

async def test():
    text = 'Can you come to the meeting online? <break time="3000ms" /> Great job.'
    c = edge_tts.Communicate(text, 'en-US-JennyNeural')
    await c.save('test_break.mp3')
    print('Generated test_break.mp3, size:', os.path.getsize('test_break.mp3'))

asyncio.run(test())
