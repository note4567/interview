from transformers import BertForQuestionAnswering, Trainer, TrainingArguments
from qa_module import set_log, pre_process

log = set_log.Log("qa_train", "./log/qa_train.text")
log.set_level(20)


if __name__ == "__main__":
    train_data = pre_process.PreProcess()
    train_data.pre_process()
    model = BertForQuestionAnswering.from_pretrained("tohoku-nlp/bert-base-japanese-v3")

    training_args = TrainingArguments(
        output_dir="./results",
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=10,
        per_device_eval_batch_size=3,
        num_train_epochs=5,
        weight_decay=0.01,
        report_to=None,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data.encoding_train,
        eval_dataset=train_data.encoding_test,
    )

    trainer.train()
