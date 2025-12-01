from flask import Flask, request, render_template, redirect, flash
from memo_core import create_memo, list_memos, update_memo, delete_memo, move_memos, rename_category, delete_category
from json_io import MEMOS_PATH, CATEGORIES_PATH, load_memos, load_categories
import datetime

app = Flask(__name__)
app.secret_key = "my_secret_key"


# sidebar
def build_sidebar_context():
    """サイドバーに必要なカテゴリ情報をまとめて返す"""
    
    categories = load_categories(CATEGORIES_PATH)
    if not categories:
        categories = ["未分類"]

    all_memos = load_memos(MEMOS_PATH)
    
    category_counts = {cat: 0 for cat in categories}

    if "未分類" not in category_counts:
        category_counts["未分類"] = 0

    for m in all_memos:
        cat = m.get("category", "").strip()
        if not cat:
            cat = "未分類"
        
        if cat not in category_counts:
            category_counts[cat] = 0
        category_counts[cat] += 1

    category_options = list(category_counts.keys())

    total_count = len(all_memos)   

    return {
        "total_count": total_count,
        "category_counts": category_counts,
        "category_options": category_options,
    }


# add
@app.route("/memos/new", methods=["GET", "POST"])
def new_memo():
    if request.method == "GET":
        sidebar_ctx = build_sidebar_context()
        return render_template(
            "new.html",
            error_message=None,
            selected_category=None,
            **sidebar_ctx,
        )
    
    if request.method == "POST":
        memo = request.form

        title = memo["title"]
        body = memo["body"]
        category = memo["category"]
        is_private = request.form.get("is_private")

        if not body:
            return render_template("new.html", error_message="本文は必ず入力してください。")
        
        if not is_private:
            is_private = False
        else:
            is_private = True

        new_memo = create_memo(MEMOS_PATH, title, body, category, is_private)

        if not new_memo:
            return render_template("new.html", error_message="登録する情報を入力してください。")
        else:
            return redirect("/memos")
        
    return render_template("new.html")

# list
@app.route("/", methods=["GET"]) # トップページはあとから新規作成に移動
@app.route("/memos", methods=["GET"])
def show_memo_list():
    category = request.args.get("category")
    sort = None

    if category == "未分類":
        category_filter = ""
    else:
        category_filter = category

    memos = list_memos(MEMOS_PATH, category_filter, sort)

    display_memos = []
    for memo in memos:
        memo = memo.copy()

        created_at = time_display_organaize(memo["created_at"])
        if not created_at:
            created_at = "(記録なし)"
        memo["created_at"] = created_at
        updated_at = time_display_organaize(memo["updated_at"])
        if not updated_at:
            updated_at = "(記録なし)"
        memo["updated_at"] = updated_at

        if not memo["category"]:
            memo["category"] = "未分類"

        display_memos.append(memo)

    # サイドバーのカテゴリ表示用
    sidebar_ctx = build_sidebar_context()

    return render_template(
        "list.html",
        memos=display_memos,
        selected_category=category,
        **sidebar_ctx,
    )


# update
@app.route("/memos/<int:memo_id>/edit", methods=["GET", "POST"])
def edit_memo(memo_id):
    if request.method == "GET":
        memos = load_memos(MEMOS_PATH)
        target_memo = None
        for memo in memos:
            int_id = int(memo["id"])
            if int_id == memo_id:
                target_memo = memo
                break
            else:
                continue

        if target_memo is None:
            flash("ご指定のメモが見つかりませんでした。")   # 編集画面の仕様上、render_tamplate だと memo や id が必要になるため redirect。しかし redirect ではメッセージを引数にできないため、flash を採用。
            return redirect("/memos")
        else:
            sidebar_ctx = build_sidebar_context()
            return render_template(
                "edit.html",
                memo=target_memo,
                memo_id=memo_id,
                error_message=None,
                selected_category=None,
                **sidebar_ctx,
            )

    if request.method == "POST":
        memos = load_memos(MEMOS_PATH)
        memo_data = None
        for m in memos:
            int_id = int(m["id"])
            if int_id == memo_id:
                memo_data = m
                break
            else:
                continue
        
        if memo_data is None:
            flash("ご指定のメモが見つかりませんでした。")   # 編集画面の仕様上、render_tamplate だと memo や id が必要になるため redirect。しかし redirect ではメッセージを引数にできないため、flash を採用。
            return redirect("/memos")

        memo = request.form

        title = memo["title"]
        body = memo["body"]
        category = memo["category"]
        # is_private = request.form.get("is_private") あとから対応予定

        if not body:
            return render_template("edit.html", memo=memo_data, memo_id=memo_id, error_message="本文は必須です。")

        up_memo = update_memo(MEMOS_PATH, memo_id, title, body, category)

        if up_memo is None:
            return render_template("edit.html", memo=memo_data, memo_id=memo_id, error_message="更新する情報がありませんでした。")
        elif up_memo is False:
            return render_template("edit.html", memo=memo_data, memo_id=memo_id, error_message="処理中にエラーが発生しました。")
        else:
            flash("メモの編集・保存に成功しました。")
            return redirect("/memos")


# delete
@app.route("/memos/<int:memo_id>/delete", methods=["GET", "POST"])
def del_memo(memo_id):
    if request.method == "GET":
        target_memo = None
        memos = load_memos(MEMOS_PATH)
        for memo in memos:
            int_id = int(memo["id"])
            if int_id == memo_id:
                target_memo = memo
                break
            else:
                continue
        
        if target_memo is None:
            flash("該当のメモはありませんでした。")
            return redirect("/memos")
        else:
            created_at =  time_display_organaize(target_memo["created_at"])
            if not created_at:
                created_at = "(記録なし)"
            updated_at =  time_display_organaize(target_memo["updated_at"])
            if not updated_at:
                updated_at = "(記録なし)"

            sidebar_ctx = build_sidebar_context()
            return render_template(
                "delete.html",
                memo=target_memo,
                memo_id=memo_id,
                created_at=created_at,
                updated_at=updated_at,
                selected_category=None,
                **sidebar_ctx,
            )
    
    if request.method == "POST":
        d_memo = delete_memo(MEMOS_PATH, memo_id)

        if d_memo is None:
            flash("削除対象のメモは存在しません。すでに削除された可能性があります。")
            return redirect("/memos")
        elif d_memo is False:
            flash("メモを削除中にエラーが起きました。")
            return redirect("/memos")
        else:
            flash(f"「{d_memo['title']}」を削除しました。")
            return redirect("/memos")
        

# select + action
@app.route("/memos/bulk", methods=["POST"])
def bulk_memos():
    selected_ids = request.form.getlist("selected_ids")
    if not selected_ids:
        flash("メモが選択されていません。")
        return redirect("/memos")
    
    action = request.form.get("action")     # delete or move

    int_ids = []
    for s in selected_ids:
        try:
            int_id = int(s)
        except ValueError:
            flash("選択したデータのIDに問題があります。")
            return redirect("/memos")
        int_ids.append(int_id)
    
    delete_count = 0
    if action == "delete":
        for delete_id in int_ids:
            result = delete_memo(MEMOS_PATH, delete_id)
            if result:
                delete_count += 1

        if delete_count > 0:
            flash(f"{delete_count}件のメモを削除しました。")
        else:
            flash("削除できるメモが見つかりませんでした。")
        return redirect("/memos")
    
    elif action == "move":
        move_category = request.form.get("move_category")
        if not move_category or move_category.strip() == "":
            flash("移動先のカテゴリ名を指定してください。")
            return redirect("/memos")
        
        moved_count = move_memos(MEMOS_PATH, int_ids, move_category)
        if moved_count > 0:
            flash(f"{moved_count} 件のメモを {move_category} へ移動しました。")
        else:
            flash("移動対象のメモが見つかりません。")
        
        return redirect("/memos")
        
    else:
        flash("「削除」または「移動」を選択してください。")
        return redirect("/memos")
    

# show_category
@app.route("/categories", methods=["GET", "POST"])
def show_categories():
    if request.method == "GET":
        sidebar_ctx = build_sidebar_context()
        return render_template(
            "categories.html",
            selected_category=None,
            category_counts=sidebar_ctx["category_counts"],
            total_count=sidebar_ctx["total_count"],
            category_options=sidebar_ctx["category_options"],
        )
    
    action = request.form.get("action")

    if action == "rename":
        old_name = request.form.get("old_name")
        new_name = request.form.get("new_name", "").strip()
        if not new_name:
            flash("新しい名前を入力してください。")
            return redirect("/categories")
        if old_name == new_name:
            flash("同じ名前のため変更されませんでした。")
            return redirect("/categories")
        
        old_key = "" if old_name == "未分類" else old_name
        
        rename_cat = rename_category(MEMOS_PATH, old_key, new_name)
        
        if rename_cat == 0:
            flash("変更はありませんでした。")
        elif rename_cat is False:
            flash("フォルダ名の編集集にエラーが発生しました。")
        else:
            flash(f"{rename_cat}件のカテゴリを編集しました。")
        
        return redirect("categories")
    
    elif action == "delete":
        target_name = request.form.get("target_name")

        if not target_name:
            flash("削除するカテゴリが指定されていません。")
            return redirect("/categories")
        
        if target_name == "未分類":
            flash("「未分類」のカテゴリは削除できません。")
            return redirect("/categories")
        
        target_key = "" if target_name == "未分類" else target_name
        
        moved_count = delete_category(MEMOS_PATH, target_key)

        if moved_count == 0:
            flash("対象のカテゴリに該当するメモはありませんでした。")
        elif moved_count is False:
            flash("カテゴリ削除中にエラーが発生しました。")
        else:
            flash(f"{moved_count}件のメモを削除しました。")

        return redirect("/categories")
    
    else:
        flash("不正な操作が指定されました。")
        return redirect("/categories")
        
# 時間の表示調整用
def time_display_organaize(arg_time):
    if not arg_time:
        return
    
    format_in = "%Y-%m-%dT%H:%M:%S.%f"
    try:
        dt_object = datetime.datetime.strptime(arg_time, format_in)
    except ValueError:
        format_in_no_micro = "%Y-%m-%dT%H:%M:%S"
        dt_object = datetime.datetime.strptime(arg_time[:19], format_in_no_micro)

    format_out = "%Y年%m月%d日/%H時%M分"
    format_datetime = dt_object.strftime(format_out)

    return format_datetime

if __name__ == "__main__":
    app.run(debug=True, port=8000)