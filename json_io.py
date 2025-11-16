# save_json / load_json

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMOS_PATH = os.path.join(BASE_DIR, "data", "memos.json")

def load_memos(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            memos = json.load(f)
            if not memos:
                return []
            return memos
        
    except FileNotFoundError:
        print("開けるファイルがありません。")
        return []
    except json.JSONDecodeError as e:
        print(f"ファイルのデータが破損しています: {e}")
        return []
    except Exception as e:
        print(f"ロード中にエラーが発生しました: {e}")
        return []
    
def save_memos(filepath, memos_list):
    try:
        dirpath = os.path.dirname(filepath)
        os.makedirs(dirpath, exist_ok=True)
        tmp_path = os.path.join(dirpath, ".memos.tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(memos_list, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, filepath)

    except Exception as e:
        print(f"書き込み中にエラーが起きました: {e}")