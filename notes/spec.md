【app.py】

必要なライブラリ
・datetime
・argparse


"add"

実行したいこと
・引数から title / body / category / is_private を受け取る
・bodyが空ならエラー表示にして終了
・categoryが未指定なら"メインフォルダ"をセットする
・is_private用のフラグが付いているか判定する（初期でFalseになるようにする）
・memo_core.create_memo()に必要な情報を渡す
・戻り値（作成されたメモや成功フラグ）を見てから結果を表示

擬似コード
1．argparseのメイン parser を作る
2．サブコマンドを管理する subparsers を作る
3．add のサブコマンドを作る
    → addサブコマンドが選ばれた場合、呼び出される処理関数をセットしておく
4．--title(任意) / --body(必須) / --category(任意) / --private(store_trueでフラグ) をオプションで受け取る
5．bodyが None or 空文字 なら「本文は必須です」と表示し終了
6．categoryが None or 空文字 なら"メインフォルダ"をセット
7．result = create_memo()を呼び出す
8．result が None でなければ「メモを追加しました」のメッセージを表示（idは載せない予定）
    → None の場合は「メモを追加できませんでした」を表示


"list"

実行したいこと
・コマンドラインから絞り込み条件を受け取り、一覧を表示する
・すべてのメモではカテゴリ関係なく全件表示（基本）
・カテゴリでのソート機能を実装
・ソート順を指定できるようにする（余裕があれば）

擬似コード
1．list のサブコマンドを作る
2．args.category(任意)を受け取る
3．if not args.category / elif args.category = "all" なら「すべてのメモ」を表示
4．args.sort(任意) を受け取る
5．sortが　None or 空文字　なら sort = updated(更新日の新しい順) で表示
6．list_memos(MEMOS_PATH, category, sort_key)を呼び出す
7．戻ってきたメモ一覧を タイトル / カテゴリ / 作成日 / 更新日 のような形式で表示（f"{memo['title']} | {memo['category']} | … "）
    → メモが0件なら「メモがありません」などのメッセージを表示


"update"

実行したいこと
・指定されたidのメモを部分的に更新する
・title / body / category のうち、指定された項目だけを書き換える
・更新の結果を表示する

擬似コード
1．update のサブコマンドを作成
2．--id(必須)と、--title / --body / --category(任意)を受け取る
3．idが指定されていなければ、「idを指定してください」と表示して終了
    → idが見つからなければ、「指定したidはありません」と表示して終了
4．title / body / category のいずれも指定がない場合もエラー終了
5．memo_core.update_memo()を呼び出す
6．成功なら「メモを更新しました」と表示
    → 失敗なら「更新できませんでした」などを表示


"delete"

実行したいこと
・指定されたidのメモを1件削除する（あとから一括削除も実装）
・--forceがあれば確認なしで削除

擬似コード
1．argparseでdeleteサブコマンドを定義
2．--id(必須)と--force(任意)を受け取る
3．idが指定されていなければエラー
4．forceが指定されていない場合は「本当に削除しますか？(y/n)」と表示
    → nが選択された場合は削除せず終了
5．memo_core.delete_memo()を呼び出す
6．成功なら「id〇〇のメモを削除しました」と表示
    → 失敗ならエラーメッセージを表示


【memo_core.py】

必要なライブラリ
・os
・json
・datetime

"create_memo(json_path, title, body, category, is_private)"

実行したいこと
・bodyの入力を受ける(必須)
・titleの入力は任意（空なら本文の先頭から10文字を代入）
・categoryも任意（なければ"メインフォルダ"とする）
・idはJSON内の最大値 + 1
・現在時刻を取得して created_at / updated_at に同じ値をセット（YYYY-MM-DDTHH:MM:SS）
    → UI側では「当日なら時刻だけ表示」「それ以外は日付だけ表示」に加工
・is_privateはフラグ扱い（デフォルトはFalse / カテゴリで分類するか検討）
・新しいメモを配列の最後に追加して保存する

疑似コード
1．json_io.load_memos()で一覧を取得
2．配列が空ならid = 1
    → 空でないなら配列中のmax + 1のidを作る
3．bodyが空かは、app.pyでチェック（ここではvalueがある前提）
4．titleが空の場合はbodyの先頭10文字をtitleとする
5．現在時刻をcreated_at / update_atに同じ値をセット(.isoformatを使用)
6．categoryが未指定(None or 空文字)なら"メインフォルダ"を割り当てる
    → if not categoryで対応
7．is_privateはFalse（あとからプライベートフォルダとして機能させる予定 / 今はapp.py側から必ずFalseが来る設定）
8．上記の項目をまとめて「1つの新しいメモ」を作成（辞書データ）
9．メモ一覧の最後に追加
10．json_io.save_memos()で保存
11．成功 or 失敗の結果(new_memo or None)を返す


"list_memos(json_path, category, sort_key)"

実行したいこと
・条件に合うメモ一覧を返す

擬似コード
1．json_io.load_memos()で一覧を取得
2．categoryが "all"（ラベル:すべてのメモ）ではなく、ほかに指定がある場合、対象のカテゴリに絞り込む
3．sort_keyの内容に応じて並び替え
4．絞り込みと並び替えをしたリストを返す
    → 0件なら空リストを返す


"update_memo(json_path, id, title, body, category)"

実行したいこと
・指定されたメモを部分的に更新する

擬似コード
1．json_io.load_memos()で一覧を取得
2．forループで入力されたidに一致するメモを探す
    → なければ False を返す
3．見つかったメモに対し、
    title が None でなければ上書き
    body が None でなければ上書き
    category が None でなければ上書き
4．現在の時刻を取得し、updated_atを上書き（.isoformat()）
5．更新済みのメモでmemos[index]を入れ替える
5．json_io.save_memos()で保存
6．成功 or 失敗の結果（memos or False）を返す


"delete_memo(json_path, id)"

実行したいこと
・指定されたメモを削除する

擬似コード
1．json_io.load_memosを呼び出す
2．入力されたidと一致するメモを探す
3．見つからなければ、Falseを返す
4．pop(index)で対象のメモを削除
5．json_io.save_memos()で保存
6．成功 or 失敗の結果（memo or False）を返す


【json_io.py】

必要なライブラリ
・os
・json

"load_memos(json_path)"

実行したいこと
・指定されたパスのJSONファイルを読み込んで、メモの一覧を返す
・ファイルが存在しない / 空などのときは、空リストを返す

擬似コード
1．json_pathにファイルがあるかチェック
2．存在するならファイルを開いてJSONを読み込む
    → 存在しなければ空リストを返す
3．読み込んだデータがリストでなければ、エラー表示
    → 問題がなければリストを返す
4．もしJSONデコードエラーが発生した場合、エラー内容を表示し空リストを返す


"save_memos(json_path, memos_list)"

実行したいこと
・メモ一覧のリストをJSONとしてファイルに保存する
・一時ファイルを作成し、安全に保存する

擬似コード
1．memos_listがリストであることを前提にする
2．一時的な保管場所を作成
3．ファイルを上書きモードで開く
4．JSON文字列に変換して一時的なファイル書き込む
5．一時的なファイルとメインのファイルを置き換える
6．保存に失敗した場合はエラーを表示