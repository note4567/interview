from transformers import BertJapaneseTokenizer  # type: ignore
from typing import Final
import set_log


log = set_log.Log("qa_toknizer", "./log/qa_toknizer.text")
log.set_level(20)


class QA_TOKENIZER(BertJapaneseTokenizer):
    """日本語用の QAトークナイザ"""

    def make_answer_pos(self, encoding, data):
        """答えの開始位置と終了位置を設定する"""

        # 読み込んだ学習用のデータから「文脈」「質問」「答え」の値を取得
        # spans の値はエンコード処理された値をそのまま受け取る
        spans = encoding["spans"]
        context = data["context"]
        answer = data["answer"]
        answer_start = data["answer_start"]

        # 答えの開始位置と終了位置の初期化
        start_positions: int = 0
        end_positions: int = 0

        # 答えの無い場合(-1)は処理しない
        if answer_start != -1:
            # 答えの長さを計算し、それを span に当てはめる
            answer_length: int = len(answer)
            answer_end: int = answer_start + answer_length
            for span in spans:
                if span[0] == answer_start:
                    # 答えの開始位置
                    start_positions: int = spans.index(span)
                if span[1] == answer_end:
                    # 答えの終了位置
                    end_positions: int = spans.index(span)

        # 答えの開始位置と終了位置を encoding にも反映させる
        encoding["start_positions"] = start_positions
        encoding["end_positions"] = end_positions

        # 答え合わせのテストをする
        result_answer: str = context[
            spans[start_positions][0] : spans[end_positions][1]  # Noqa
        ]

        if answer != result_answer:
            # 答え合わせが間違っている場合は例外を発生させる
            log.logger.info(f"[Error]: {data =}")
            raise

        del encoding["spans"]

        return encoding

    def encode_bert(self, data, training=True):
        """エンコード処理"""

        # 文脈につき、通常のトークンを追加するリスト
        tokens: list = []

        # 文脈につき、トークンに対応する文章中の文字列を追加するリスト
        # (文章中の文字列なので [UNK]は置き換えられ、##は取り除かれた状態)
        tokens_original: list = []

        # 質問のトークンを追加するリスト
        question_tokens: list = []

        # 学習用データから「文脈」と「質問」を設定する
        context = data["context"]
        question = data["question"]

        # 上限文字数の設定
        if len(context) > 512:
            log.logger.error(f"[ Too many] {context =}")
            raise

        # MeCabで単語に分割(質問)
        for q in self.word_tokenizer.tokenize(question):
            question_tokens.extend(self.subword_tokenizer.tokenize(q))

        # MeCabで単語に分割(文脈)
        words = self.word_tokenizer.tokenize(context)

        # tokens と tokens_original に値を詰める
        for word in words:
            # 単語をサブワードに分割
            tokens_word = self.subword_tokenizer.tokenize(word)
            tokens.extend(tokens_word)

            # 未知語への対応
            if tokens_word[0] == "[UNK]":
                log.logger.info("UNK")
                tokens_original.append(word)
            else:
                tokens_original.extend(
                    [token.replace("##", "") for token in tokens_word]
                )

        # ----- 文字列の位置を調べる(tokens_original を対象にする) -----
        # 文脈を切り取る位置の初期化
        position = 0

        # 文字列の位置を追加するリスト
        spans: list = []

        # span に token の位置を設定する
        for token in tokens_original:
            length: int = len(token)
            # 文脈から position により切り取られた値と token が等しいかの判定
            while True:
                if token != context[position : position + length]:  # Noqa
                    # context に空白がある場合
                    position += 1
                else:
                    spans.append([position, position + length])
                    position += length
                    break

        # 符号化処理
        input_ids = self.convert_tokens_to_ids(tokens)
        q = self.convert_tokens_to_ids(question_tokens)
        encoding = self.prepare_for_model(
            q, input_ids, max_length=500, padding="max_length", truncation=True
        )

        # 推論時はここで返す
        if not training:
            return encoding

        # ----- 学習時は span の処理をする -----
        # padding の設定
        pad_num: int = (
            len(encoding["input_ids"]) - len(spans) - len(question_tokens) - 3
        )
        _CLS: Final[list[list[int]]] = [[-1, -1]]
        _SEP: Final[list[list[int]]] = [[-1, -1]]
        _PAD: Final[list[list[int]]] = [[-1, -1]] * pad_num

        # 質問の長さも含める
        question_length: int = len(question_tokens)

        spans = _CLS + [[-1, -1]] * question_length + _SEP + spans + _SEP + _PAD
        encoding["spans"] = spans

        return self.make_answer_pos(encoding, data)
