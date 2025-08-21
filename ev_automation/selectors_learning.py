import json
import os


DEFAULT_LEARNED_FILE = "D:/Project/AutoClick/learned_selectors.json"


def load_learned_selectors(path: str = DEFAULT_LEARNED_FILE):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_learned_selector(field_name: str, selectors: list[str], path: str = DEFAULT_LEARNED_FILE):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = load_learned_selectors(path)
        data[field_name] = selectors
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


