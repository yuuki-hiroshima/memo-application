# argparse

from memo_core import create_memo, list_memos, update_memo, delete_memo
from json_io import MEMOS_PATH, load_memos
import argparse
import datetime

def parse_args():
    parser = argparse.ArgumentParser(
        description="メモアプリ\nadd / list / update / delete を使って操作できます。",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="利用できるコマンド")

    # add
    parse_add = subparsers.add_parser("add", help="メモを作成")
    parse_add.add_argument("--title", help="タイトルを入力")
    parse_add.add_argument("--body", help="本文を入力")
    parse_add.add_argument("--category", help="カテゴリーを入力")
    parse_add.add_argument("--is_private", action="store_true", help="プライバシー設定の有無")
    parse_add.set_defaults(func=handle_add)

    # list
    parse_list = subparsers.add_parser("list", help="メモの一覧を表示")
    parse_list.add_argument("--category", help="カテゴリーを入力")
    parse_list.add_argument("--sort", help="更新時間を基準に並び替えます。asc=昇順 / desc=降順")
    parse_list.set_defaults(func=handle_list)

    # update
    parse_update = subparsers.add_parser("update", help="メモを編集")
    parse_update.add_argument("--id", help="idを入力")
    parse_update.add_argument("--title", help="タイトルを入力")
    parse_update.add_argument("--body", help="本文を入力")
    parse_update.add_argument("--category", help="カテゴリーを入力")
    parse_update.set_defaults(func=handle_update)

    # delete
    parse_delete = subparsers.add_parser("delete", help="メモを削除")
    parse_delete.add_argument("--id", help="idを入力")
    parse_delete.add_argument("--force", action="store_true", help="削除の確認をスキップ")
    parse_delete.set_defaults(func=handle_delete)

    return parser.parse_args()

# 新規作成
def handle_add(args):
    print(args)
    if not args.body:
        print("本文を入力してください。")

    if not args.category:
        args.category = "メインフォルダ"

    result = create_memo(MEMOS_PATH, args.title, args.body, args.category, args.is_private)

    if result is not None:
        print("メモを追加しました。")
    else:
        print("メモを追加できませんでした。")

# 一覧表示
def handle_list(args):
    category = args.category
    sort = args.sort

    result = list_memos(MEMOS_PATH, category, sort)

    if not result:
        print("該当するメモがありません。")
    else:
        for memo in result:

            original_datetime = memo['updated_at']
            format_in = "%Y-%m-%dT%H:%M:%S.%f"
            try:
                dt_object = datetime.datetime.strptime(original_datetime, format_in)
            except ValueError:
                format_in_no_micro = "%Y-%m-%dT%H:%M:%S"
                dt_object = datetime.datetime.strptime(original_datetime[:19], format_in_no_micro)
            
            format_out = "%Y年%m月%d日/%H時%M分"
            format_datetime = dt_object.strftime(format_out)

            print(f"{memo['id']} | {memo['title']} | {memo['body'][:10]} | {memo['category']} | {format_datetime}")

# 編集
def handle_update(args):
    try:
        if not args.id:
            print("IDを入力してください。listで確認できます。")
            return
        else:
            int_id = int(args.id)
    except (TypeError, ValueError):
        print("数字を入力してください。")
        return

    if not args.title and not args.body and not args.category:
        print("更新する情報が入力されていません。")
        return
    else:
        title = args.title
        body = args.body
        category = args.category

        update_result = update_memo(MEMOS_PATH, int_id, title, body, category)

        if not update_result:
            print("対象となるメモがありません。listで確認してください。")
        else:
            print("メモの更新ができました。更新したデータは以下の内容です。")
            original_datetime = update_result['updated_at']
            format_in = "%Y-%m-%dT%H:%M:%S.%f"
            try:
                dt_object = datetime.datetime.strptime(original_datetime, format_in)
            except ValueError:
                format_in_no_micro = "%Y-%m-%dT%H:%M:%S"
                dt_object = datetime.datetime.strptime(original_datetime[:19], format_in_no_micro)
            
            format_out = "%Y年%m月%d日/%H時%M分"
            format_datetime = dt_object.strftime(format_out)

            print(f"{update_result['id']} | {update_result['title']} | {update_result['body'][:10]} | {update_result['category']} | {format_datetime}")

# 削除
def handle_delete(args):
    try:
        if not args.id:
            print("IDを入力してください。listで確認できます。")
            return
        else:
            int_id = int(args.id)

    except (TypeError, ValueError):
        print("数字を入力してください。listで確認できます。")
        return
    
    if args.force:
        delete = delete_memo(MEMOS_PATH, int_id)
        if delete is None:
            print("IDに該当するメモはありません。listで確認できます。")
        elif delete == False:
            return
        else:
            print(f"{delete['id']} | {delete['title']} | {delete['body'][:10]}を削除しました。")
    else:
        memos = load_memos(MEMOS_PATH)
        
        check_memo = None
        for memo in memos:
            if memo["id"] == int_id:
                check_memo = memo
                break
            else:
                continue
        
        if check_memo is None:
            print("IDに該当するメモはありません。listで確認できます。")
            return

        choice_yn = input(f"ID: {check_memo['id']} | {check_memo['title']} | {check_memo['body'][:10]} を削除しますか？（y/n）:")
        choice = choice_yn.strip().lower()

        if choice == "y":
            delete = delete_memo(MEMOS_PATH, int_id)
            if delete is None:
                print("IDに該当するメモはありません。listで確認できます。")
            elif delete == False:
                return
            else:
                print(f"{delete['id']} | {delete['title']} | {delete['body'][:10]}を削除しました。")
        elif choice == "n":
            print("削除の操作を取りやめます。")
            return
        else:
            print("y/nのいずれかを入力してください。")
            return    

# 実行
def main():
    args = parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("コマンドを指定してください（ add / list/ update / delete ）")

if __name__ == "__main__":
    main()