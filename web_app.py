from flask import Flask, request, render_template, redirect, flash
from memo_core import create_memo, list_memos, update_memo, delete_memo
from json_io import MEMOS_PATH, load_memos
import datetime

app = Flask(__name__)
app.secret_key = "my_secret_key"

# add
@app.route("/memos/new", methods=["GET", "POST"])
def new_memo():
    if request.method == "GET":
        return render_template("new.html")
    
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
    all_memos = load_memos(MEMOS_PATH)
    category_counts = {}
    for m in all_memos:
        cat = m["category"]
        if not cat:
            cat = "未分類"
        category_counts[cat] = category_counts.get(cat, 0) + 1  # 取得したカテゴリをkeyとし、valueに1ずつ追加していく → {"仕事": 1, "おもちゃ": 4, "食事": 2}

    total_count = len(all_memos)

    return render_template(
        "list.html",
        memos=display_memos,
        total_count=total_count,
        category_counts=category_counts,
        selected_category=category
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
            return render_template("edit.html", memo=target_memo, memo_id=memo_id)

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

            return render_template(
                "delete.html",
                memo=target_memo,
                memo_id=memo_id,
                created_at=created_at,
                updated_at=updated_at
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