from transformers import BertForQuestionAnswering
from qa_module import set_log, qa_toknizer
import json
import re
import torch  # type: ignore
import random

log = set_log.Log("inference", "./log/inference.text")
log.set_level(20)

# トークナイザ
toknizer = qa_toknizer.QA_TOKENIZER
tohoku_tk = toknizer.from_pretrained("tohoku-nlp/bert-base-japanese-v3")

# 学習したモデルを読み込む
model = BertForQuestionAnswering.from_pretrained("./checkpoint-3490", from_tf=False)

# 質問と文脈の準備
test_file_path = "train/test.json"
with open(test_file_path) as json_file:
    test_data: dict = json.load(json_file)

random.shuffle(test_data)

# 正解・不正解を数えるカウンター
correct_counter = 0
incorrect_counter = 0
total_num = len(test_data)

# 推論処理
for data in test_data[:10]:
    # 符号化処理
    inputs = tohoku_tk.encode_bert(data, training=False)
    inputs = {k: torch.tensor([v]).to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    # 出力される start_logits と end_logits を使って、答えの開始位置と終了位置を抽出
    start_scores = outputs.start_logits
    end_scores = outputs.end_logits

    # 開始位置と終了位置を決定
    start_index = torch.argmax(start_scores)
    end_index = torch.argmax(end_scores)

    # 答えを抽出
    inputs = inputs["input_ids"].tolist()[0]
    answer_tokens = inputs[start_index : end_index + 1]  # type: ignore # Noqa
    answer = tohoku_tk.convert_tokens_to_string(
        tohoku_tk.convert_ids_to_tokens(answer_tokens)
    )

    # 回答のノイズを除去する
    answer: str = re.sub(r"\s", "", answer)
    answer: str = re.sub(r"\[CLS\]", "", answer)
    answer: str = re.sub(r"^##", "", answer)

    if answer == data["answer"]:
        correct_counter += 1
        log.logger.info(f"文脈: {data['context']}")
        log.logger.info("-" * 75)
        log.logger.info(f"質問: {data['question']}")
        log.logger.info(f"答え: {answer}")
        log.logger.info(f"正解: {data['answer']}")
        log.logger.info("判定: [正解]\n")
    else:
        incorrect_counter += 1
        log.logger.info(f"Incorrect: [不正解数] {incorrect_counter}")
        log.logger.error(f"文脈: {data['context']}")
        log.logger.error(f"質問: {data['question']}")
        log.logger.error(f"正解: {data['answer']}")
        log.logger.error(f"答え: {answer}")
        log.logger.info("判定: [不正解]\n")

log.logger.info(f"[正解率] {correct_counter / total_num}")
log.logger.info(f"[不正解率] {incorrect_counter / total_num}")
