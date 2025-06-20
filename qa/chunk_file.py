"""データを集約するスクリプト
学習用のデータは、ブランド毎(20個のブランド)に取得しているので 1ヶ所に集める
その際に、ブランド毎にデータ量の偏りを無くすため、件数の目安を設定する

学習用データ: 1ブランドにつき 350件程度
検証用データ: 1ブランドにつき 120件程度
テストデータ: 特に制限は無い"""

import json
import set_log
import glob


log = set_log.Log("chunk_file", "./log/chunk_file.text")
log.set_level(20)


def make_chunk(handle) -> list:
    """読み込んだデータを上限件数で切り取る
    ファイルはブランド毎に読み込むので、切り取ったデータを集約する"""

    out_data: list = []
    for file_path in handle["input_files"]:
        with open(file_path, encoding="utf-8") as file:
            log.logger.info(file_path)

            content: str = file.read()
            chunk: list = json.loads(content)[: handle["chunk_range"]]
            out_data.extend(chunk)

    return out_data


if __name__ == "__main__":
    # 読み込むファイル
    INPUT_TRAIN: str = "./crawl/data/*train.json"
    INPUT_DEV: str = "./crawl/data/*dev.json"
    INPUT_TEST: str = "./crawl/data/*test.json"

    # 指定したディレクトリ内のすべてのファイルを取得
    train_files: list[str] = glob.glob(f"{INPUT_TRAIN}")
    dev_files: list[str] = glob.glob(f"{INPUT_DEV}")
    test_files: list[str] = glob.glob(f"{INPUT_TEST}")

    # 出力先のパス
    OUT_TRAIN_FILE: str = "./train/train.json"
    OUT_DEV_FILE: str = "./train/dev.json"
    OUT_TEST_FILE: str = "./train/test.json"

    # 学習データの偏りをなくすため上限を設定する
    file_handles: list[dict] = [
        {"out_path": OUT_TRAIN_FILE, "input_files": train_files, "chunk_range": 350},
        {"out_path": OUT_DEV_FILE, "input_files": dev_files, "chunk_range": 120},
        {"out_path": OUT_TEST_FILE, "input_files": test_files, "chunk_range": None},
    ]

    # 件数を調整後のファイルを格納する
    out_data: list = []

    # QAモデルで使用するデータを作成
    for handle in file_handles:
        out_data = make_chunk(handle)

        with open(handle["out_path"], "w", encoding="utf-8") as f:
            json.dump(out_data, f, ensure_ascii=False, indent=4)
