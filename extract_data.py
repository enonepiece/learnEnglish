import json
import re

content_path = r"C:\Users\Andrew\.gemini\antigravity-ide\brain\6681c34d-4474-4339-ad4b-2bde471265fb\.system_generated\steps\7\content.md"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'<script id="data" type="application/json">(\[.*?\])</script>', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print(f"Extracted {len(data)} words successfully!")
    with open("ogden_850_full.json", "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
else:
    print("Not found")
