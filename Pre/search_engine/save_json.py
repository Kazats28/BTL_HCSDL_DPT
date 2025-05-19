import json

def save_json(PATH, TEXT):
    with open(PATH + ".json", "w", encoding="utf-8") as f:
        json.dump(TEXT, f, ensure_ascii=False, indent=2)