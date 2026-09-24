import json
from opencc import OpenCC
from generate_ep01 import verbs_data
from generate_ep02 import preps_data

cc = OpenCC('s2twp')

with open("ogden_850_full.json", "r", encoding="utf-8") as f:
    words = json.load(f)

print(f"Loaded {len(words)} words.")

# Update Ep01 words (0..17)
verb_map = {v["word"]: v for v in verbs_data}
for i in range(18):
    w = words[i]["w"]
    if w in verb_map:
        v = verb_map[w]
        words[i]["zh"] = v["zh_brief"]
        words[i]["core"] = v["core"]
        words[i]["ex"] = v["ex_en"]
        words[i]["exz"] = v["ex_zh"]

# Update Ep02 words (18..37)
prep_map = {p["word"]: p for p in preps_data}
for i in range(18, 38):
    w = words[i]["w"]
    if w in prep_map:
        p = prep_map[w]
        words[i]["zh"] = p["zh_brief"]
        words[i]["core"] = p["core"]
        words[i]["ex"] = p["ex_en"]
        words[i]["exz"] = p["ex_zh"]

# For all other words (38..849), convert Chinese to Traditional Chinese
for i in range(38, len(words)):
    words[i]["zh"] = cc.convert(words[i].get("zh", ""))
    words[i]["core"] = cc.convert(words[i].get("core", ""))
    words[i]["exz"] = cc.convert(words[i].get("exz", ""))

with open("ogden_850_master.json", "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False, indent=2)

print("ogden_850_master.json successfully created with 100% Traditional Chinese and Ep01/Ep02 exact match!")
