from typing import Final
from datasets import load_dataset  # type: ignore
from . import qa_toknizer, set_log
import glob

log = set_log.Log("pre_process", "./log/pre_process.text")
log.set_level(20)


class PreProcess:
    """エンコーディング処理を行う"""

    def __init__(self) -> None:
        # 学習用のデータのパス
        self.INPUT_TRAIN: str[Final] = "./train/train.json"
        self.INPUT_DEV: str[Final] = "./train/dev.json"
        self.encoding_train = None
        self.encoding_test = None
        self.toknizer = qa_toknizer.QA_TOKENIZER

    def pre_process(self) -> None:
        # 指定したディレクトリ内のすべてのファイルを取得
        train_file: list[str] = glob.glob(f"{self.INPUT_TRAIN}")
        dev_file: list[str] = glob.glob(f"{self.INPUT_DEV}")

        # データセット処理
        dataset_train = load_dataset("json", data_files=train_file)
        dataset_dev = load_dataset("json", data_files=dev_file)

        # トークナイザの設定
        tohoku_tk = self.toknizer.from_pretrained("tohoku-nlp/bert-base-japanese-v3")

        # エンコーディング処理(train データ)
        self.encoding_train = dataset_train["train"].map(
            tohoku_tk.encode_bert,
            remove_columns=dataset_train["train"].column_names,
        )

        # エンコーディング処理(検証 データ)
        self.encoding_test = dataset_dev["train"].map(
            tohoku_tk.encode_bert, remove_columns=dataset_dev["train"].column_names
        )
