# 動作確認用のファイル（完成後は削除予定）


from json_io import MEMOS_PATH, load_memos, save_memos

bad = load_memos(MEMOS_PATH)
print(bad)