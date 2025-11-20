from flask import Flask, request, render_template, redirect, flash
from memo_core import create_memo, list_memos, update_memo, delete_memo
from json_io import MEMOS_PATH, load_memos

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

# list
@app.route("/", methods=["GET"]) # トップページはあとから新規作成に移動
@app.route("/memos", methods=["GET"])
def show_memo_list():
    category = None
    sort = None

    memos = list_memos(MEMOS_PATH, category, sort)

    return render_template("list.html", memos=memos)


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

if __name__ == "__main__":
    app.run(debug=True, port=8000)