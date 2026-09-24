import json

with open("ogden_850_master.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# Fix word 2 (get)
words[1]["core"] = "核心意象是：把東西收到手裡，或讓狀態變成新的樣子。它是萬能動詞，能代替獲得、收到或轉變為等概念。"

# Fix word 185 (development)
if len(words) > 184 and words[184]["w"] == "development":
    words[184]["exz"] = words[184]["exz"].replace("AI", "人工智慧")

with open("ogden_850_master.json", "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False, indent=2)

print("Updated ogden_850_master.json successfully.")
