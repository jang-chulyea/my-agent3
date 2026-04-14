import json


def load_exam(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["problems"]
