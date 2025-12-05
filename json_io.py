# save_json / load_json

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMOS_PATH = os.path.join(BASE_DIR, "data", "memos.json")
CATEGORIES_PATH = os.path.join(BASE_DIR, "data", "categories.json")
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")

def load_memos(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            memos = json.load(f)
            if not memos:
                return []
            return memos
        
    except FileNotFoundError:
        print("開けるファイルがありません。")
    except json.JSONDecodeError as e:
        print(f"ファイルのデータが破損しています: {e}")
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

def load_categories(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            categories = json.load(f)

            if not categories:
                return []
            return categories
        
    except FileNotFoundError:
        print("開けるファイルがありません。")
    except json.JSONDecodeError as e:
        print(f"ファイルのデータが破損しています: {e}")
    except Exception as e:
        print(f"ロード中にエラーが発生しました: {e}")

    return []

def save_categories(filepath, category_list):
    try:
        dirpath = os.path.dirname(filepath)
        os.makedirs(dirpath, exist_ok=True)
        tmp_path = os.path.join(dirpath, ".categories.tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(category_list, f, ensure_ascii=False, indent=2)
        
        os.replace(tmp_path, filepath)

    except Exception as e:
        print(f"書き込み中にエラーが起きました: {e}")


def load_settings(filepath):
    """アプリ全体の設定（辞書）を読み込む。なければ空の dict を返す。"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
           settings = json.load(f)
           if not isinstance(settings, dict):
               return {}
           return settings
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"settings.json のデータが破損しています: {e}")
        return {}
    except Exception as e:
        print(f"設定ロード中にエラーが発生しました: {e}")
        return {}

def save_settings(filepath, settings_dict):
    """設定を辞書のまま JSON に保存する。"""
    try:
        dirpath = os.path.dirname(filepath)
        os.makedirs(dirpath, exist_ok=True)
        tmp_path = os.path.join(dirpath, ".settings.tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, filepath)
    except Exception as e:
        print(f"設定書き込み中にエラーが起きました: {e}")