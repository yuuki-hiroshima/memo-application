from flask import Flask, request, render_template, redirect, flash, session
from memo_core import create_memo, list_memos, update_memo, delete_memo, move_memos, rename_category, delete_category
from json_io import MEMOS_PATH, CATEGORIES_PATH, SETTINGS_PATH, load_memos, load_categories, save_categories, load_settings, save_settings
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

    public_memos = [m for m in all_memos if not m.get("is_private")]
    
    category_counts = {cat: 0 for cat in categories}

    if "未分類" not in category_counts:
        category_counts["未分類"] = 0

    for m in public_memos:
        cat = m.get("category", "").strip()
        if not cat:
            cat = "未分類"
        
        if cat not in category_counts:
            category_counts[cat] = 0
        category_counts[cat] += 1

    sorted_items = sorted(
        category_counts.items(),
        key=lambda item: (item[0] != "未分類", item[0])
    )
    category_counts_sorted = dict(sorted_items)
    category_options = list(category_counts_sorted.keys())

    total_public_count = len(public_memos)  

    private_count = sum(1 for m in all_memos if m.get("is_private"))

    # サイドバーの表示順を決める。
    # 未分類 → 未分類以外 → メモにだけ存在するカテゴリ（念のため）
    sidebar_categories = [] 

    if "未分類" in category_counts:
        sidebar_categories.append("未分類")

    for cat in categories:
        if cat != "未分類" and cat in category_counts:
            sidebar_categories.append(cat)

    for cat in category_counts.keys():
        if cat not in sidebar_categories:
            sidebar_categories.append(cat)


    return {
        "total_count": total_public_count,
        "category_counts": category_counts_sorted,
        "category_options": category_options,
        "private_count": private_count,
        "sidebar_categories": sidebar_categories,
    }

# load_private_password
DEFAULT_PRIVATE_PASSWORD = "0000"
def get_private_password():
    """settings.json から現在のプライベートパスワードを取得。なければ初期値で作る。""" 
    settings = load_settings(SETTINGS_PATH)
    pw = settings.get("private_password")

    if not pw:
        pw = DEFAULT_PRIVATE_PASSWORD
        settings["private_password"] = pw
        save_settings(SETTINGS_PATH, settings)

    return pw

# save_private_password
def set_private_password(new_password: str):
    """新しいパスワードを settings.json に保存する。"""
    settings = load_settings(SETTINGS_PATH)
    settings["private_password"] = new_password
    save_settings(SETTINGS_PATH, settings)

# add
@app.route("/", methods=["GET"])
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
            flash("1件のメモを登録しました。")
            return redirect("/memos")
        
    return render_template("new.html")

# list
@app.route("/memos", methods=["GET"])
def show_memo_list():
    category = request.args.get("category")
    sort = None

    all_memos = load_memos(MEMOS_PATH)
    public_memos = [m for m in all_memos if not m.get("is_private")]

    if category is None:
        target_memos = public_memos

    elif category == "未分類":
        target_memos = [
            m for m in public_memos
            if (m.get("category") or "").strip() in ("", "未分類")
        ]
    
    else:
        target_memos = [
            m for m in public_memos
            if (m.get("category") or "").strip() == category
        ]

    memos_for_view = []

    for memo in target_memos:
        m = memo.copy()

        created_at = time_display_organaize(m.get("created_at"))
        if not created_at:
            created_at = "(記録なし)"
        m["created_at"] = created_at
        updated_at = time_display_organaize(m.get("updated_at"))
        if not updated_at:
            updated_at = "(記録なし)"
        m["updated_at"] = updated_at

        # 古いデータ対応用（空白を排除）。問題がなくなったら削除してもOK
        if not (m.get("category") or "").strip():
            m["category"] = "未分類"

        memos_for_view.append(m)

    # サイドバーのカテゴリ表示用
    sidebar_ctx = build_sidebar_context()

    return render_template(
        "list.html",
        memos=memos_for_view,
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
        raw = request.form.get("is_private")
        if raw is None:
            is_private = False
        else:
            is_private = True

        if not body:
            return render_template("edit.html", memo=memo_data, memo_id=memo_id, error_message="本文は必須です。")

        up_memo = update_memo(MEMOS_PATH, memo_id, title, body, category, is_private)

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
            **sidebar_ctx,
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

        categories = load_categories(CATEGORIES_PATH)

        for i, cat in enumerate(categories):
            if cat == old_name:
                categories[i] = new_name
        
        save_categories(CATEGORIES_PATH, categories)
        
        if rename_cat is False:
            flash("フォルダ名の編集集にエラーが発生しました。")
        elif rename_cat == 0:
            flash("変更はありませんでした（「未分類」は変更できません）。")
        else:
            flash(f"{rename_cat}件のカテゴリを編集しました。")
        
        return redirect("/categories")
    
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

        categories = load_categories(CATEGORIES_PATH)

        if target_name in categories:
            categories.remove(target_name)
            save_categories(CATEGORIES_PATH, categories)
        else:
            flash("カテゴリ一覧に該当の名前がありませんでした（データがズレている可能性があります）。")

        if moved_count is False:
            flash("カテゴリ削除中にエラーが発生しました。")
        elif moved_count == 0:
            flash("対象のカテゴリに該当するメモはありませんでした。")
        else:
            flash(f"{moved_count}件のメモを削除しました。")

        return redirect("/categories")
    
    elif action == "create":
        new_category = (request.form.get("new_category") or "").strip()
        if new_category == "":
            flash(f"新しい名前を入力してください。")
            return redirect("/categories")

        category_list = load_categories(CATEGORIES_PATH)

        if new_category in category_list:
            flash("すでに同じ名前が存在します。")
            return redirect("/categories")
        
        if new_category in ("未分類", "すべてのメモ"):
            flash("この名前は使用できません。")
            return redirect("/categories")
        
        category_list.append(new_category)
        save_categories(CATEGORIES_PATH, category_list)

        flash(f"「{new_category}」をフォルダを作成しました。")
        return redirect("/categories")
    
    else:
        flash("不正な操作が指定されました。")
        return redirect("/categories")
    

# パスワード変更画面（プライベートフォルダ用）
@app.route("/password", methods=["GET", "POST"])
def manege_password():
    sidebar_ctx = build_sidebar_context()

    if request.method == "GET":
        return render_template("password.html", **sidebar_ctx)
    
    current = (request.form.get("current_password") or "").strip()
    new1 = (request.form.get("new_password") or "").strip()
    new2 = (request.form.get("new_password_confirm") or "").strip()

    if current != get_private_password():
        flash("現在のパスワードが違います。")
        return redirect("/password")

    if not new1:
        flash("新しいパスワードを入力してください。")
        return redirect("/password")

    if new1 != new2:
        flash("新しいパスワード（確認）が一致しません。")
        return redirect("/password")
    
    set_private_password(new1)
    session["private_unlocked"] = False

    flash("パスワードを変更しました。再度プライベートを開くには、新しいパスワードを入力してください。")
    return redirect("/private")

# プライベートフォルダ
@app.route("/private", methods=["GET", "POST"])
def private_memos():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == get_private_password():
            session["private_unlocked"] = True
        else:
            flash("パスワードが違います。")
            sidebar_ctx = build_sidebar_context()
            return render_template("private.html", memos=None, **sidebar_ctx)
    
    if not session.get("private_unlocked"):
        sidebar_ctx = build_sidebar_context()
        return render_template("private.html", memos=None, **sidebar_ctx)

    all_memos = load_memos(MEMOS_PATH)
    private_memo_list = [m for m in all_memos if m.get("is_private")]

    if not private_memo_list:
        flash("プライベートフォルダは0件です。")
        return redirect("/memos")
    else:
        display_memos = []
        for memo in private_memo_list:
            m = memo.copy()
            created_at = time_display_organaize(m["created_at"])
            if not created_at:
                created_at = "(記録なし)"
            m["created_at"] = created_at

            updated_at = time_display_organaize(m["updated_at"])
            if not updated_at:
                updated_at = "(記録なし)"
            m["updated_at"] = updated_at

            display_memos.append(m)

    sidebar_ctx = build_sidebar_context()
    return render_template("private.html", memos=display_memos, **sidebar_ctx)
        
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