# 動作確認用のファイル（完成後は削除予定）


# 小学生向けコメント：
# memo_core から create_memo 関数を、json_io から MEMOS_PATH と load_memos を使います。
from memo_core import delete_memo
from json_io import MEMOS_PATH, load_memos, save_memos  # ファイルの場所と読み書きの道具

delete_memo(MEMOS_PATH, 1)