# add / list / update / delete

from datetime import datetime
from json_io import  save_memos, load_memos

def create_memo(filepath, title, body, category, is_private):
    try:
        memos = load_memos(filepath)
        if not memos:
            id = 1
        else:
            id_list = [memo["id"] for memo in memos]
            id = max(id_list) + 1
        print(f"取得したid：{id}")

        if not title:
            title = body[:10]

        now = datetime.now().isoformat()

        if not category:
            category = "未分類"

        new_memo = {
            "id": id,
            "title": title,
            "body": body,
            "category": category,
            "is_private": is_private,
            "created_at": now,
            "updated_at": now
        }

        new_list = [m for m in memos]
        new_list.append(new_memo)
        
        save_memos(filepath, new_list)
        return new_memo
    
    except (TypeError, ValueError):
        print("入力した文字に問題があります。")
        return
    except Exception as e:
        print(f"新規作成中にエラーが発生しました: {e}")
        return
    

def list_memos(filepath, category, sort):
    memos = load_memos(filepath)
    if not memos:
        return []
    
    if category is None:
        target = memos
    else:
        target = [memo for memo in memos if memo["category"] == category]

    if sort == "asc":
        sorted_target = sorted(
                target,
                key=lambda memo: memo["updated_at"],
                reverse=False
            )
        return sorted_target
    elif sort == "desc":
        sorted_target = sorted(
                target,
                key=lambda memo: memo["updated_at"],
                reverse=True
            )
        return sorted_target
    else:
        return target


def update_memo(filepath, id, title, body, category, is_private):
    try:
        memos = load_memos(filepath)
        for memo in memos:
            if memo["id"] == id:
                target_memo = memo
            else:
                continue
            
            if title is not None:
                target_memo["title"] = title

            if body is not None:
                target_memo["body"] = body

            if category is not None:
                category = category.strip()
                if not category:
                    category = "未分類"
                target_memo["category"] = category

            if is_private is not None:
                target_memo["is_private"] = is_private

            now = datetime.now().isoformat()
            target_memo["updated_at"] = now
            
            save_memos(filepath, memos)
            return target_memo
        
        return
        
    except (TypeError, ValueError):
        print("無効な文字が含まれています。")
        return False
    except Exception as e:
        print(f"編集集にエラーが発生しました: {e}")
        return False
    

def delete_memo(filepath, id):
    print("削除プログラムを実行します。")
    try:
        found_index = None
        found_memo = None
        memos = load_memos(filepath)
        for index, memo in enumerate(memos):
            if memo["id"] == id:
                found_index = index
                found_memo = memo
                break
            else:
                continue

        if found_index is None:
            print("削除する番号がありません。")
            return

        memos.pop(found_index)
        save_memos(filepath, memos)
        return found_memo
    
    except Exception as e:
        print(f"メモを削除中にエラーが発生しました: {e}")
        return False
    

def move_memos(filepath, id_list, new_category):
    try:
        memos = load_memos(filepath)
        if not memos:
            return 0

        moved_count = 0
        now = datetime.now().isoformat()
        for memo in memos:
            if memo["id"] in id_list:
                memo["category"] = new_category
                memo["updated_at"] = now 
                moved_count += 1
            else:
                continue

        if moved_count > 0:
            save_memos(filepath, memos)

        return moved_count
    
    except Exception as e:
        print(f"フォルダの移動中にエラーが発生しました: {e}")
        return False
    

def rename_category(filepath, old_name, new_name):
    try:
        if old_name == new_name:
            return 0
        
        memos = load_memos(filepath)
        if not memos:
            return 0

        rename_count = 0
        now = datetime.now().isoformat()
        for memo in memos:
            if memo["category"] == old_name:
                memo["category"] = new_name
                memo["updated_at"] = now
                rename_count += 1
            else:
                continue

        if rename_count > 0:
            save_memos(filepath, memos)

        return rename_count
    
    except Exception as e:
        print(f"フォルダ名の編集中にエラーが発生しました: {e}")
        return False
    

def delete_category(filepath, target_name, fallback=None):
    try:
        if fallback is None:
            fallback = "未分類"

        memos = load_memos(filepath)
        if not memos:
            return 0

        change_category_count = 0
        now = datetime.now().isoformat()
        for memo in memos:
            if memo["category"] == target_name:
                memo["category"] = fallback
                memo["updated_at"] = now
                change_category_count += 1
            else:
                continue

        if change_category_count > 0:
            save_memos(filepath, memos)
        
        return change_category_count
    
    except Exception as e:
        print(f"カテゴリの削除中にエラーが発生しました: {e}")
        return False