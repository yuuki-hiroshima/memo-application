from flask import Flask, request, render_template
from memo_core import create_memo, list_memos, update_memo, delete_memo
from json_io import MEMOS_PATH

app = Flask(__name__)


@app.route("/", methods=["GET"]) # トップページはあとから新規作成に移動
@app.route("/memos", methods=["GET"])
def show_memo_list():
    category = None
    sort = None

    memos = list_memos(MEMOS_PATH, category, sort)

    return render_template("list.html", memos=memos)

if __name__ == "__main__":
    app.run(debug=True, port=8000)