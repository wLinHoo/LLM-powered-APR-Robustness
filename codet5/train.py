import json
from sklearn.model_selection import train_test_split
import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import Dataset, DatasetDict
from transformers import DataCollatorForSeq2Seq
from accelerate import Accelerator

def main():
    # 初始化accelerator
    accelerator = Accelerator()

    # 加载数据
    with open("generate_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)["data"]

    # 划分数据集：80% 训练集，10% 验证集，10% 测试集
    train_data, temp_data = train_test_split(data, test_size=0.2, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

    # 构造 Dataset 对象
    train_dataset = Dataset.from_dict({"data": train_data})
    val_dataset = Dataset.from_dict({"data": val_data})
    test_dataset = Dataset.from_dict({"data": test_data})

    # 构造 DatasetDict 对象
    datasets = DatasetDict({
        "train": train_dataset,
        "validation": val_dataset,
        "test": test_dataset
    })

    # 加载预训练的 CodeT5-base 模型和 tokenizer
    model_name = "codet5-base"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # 数据预处理
    def preprocess_function(examples):
        inputs = [ex['input_text'] for ex in examples['data']]
        targets = [ex['target_text'] for ex in examples['data']]
        model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")

        # 设置目标（labels）
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(targets, max_length=512, truncation=True, padding="max_length")

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_datasets = datasets.map(preprocess_function, batched=True)

    # 定义数据collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # 训练参数
    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy='epoch',
        save_strategy='epoch',  # 确保保存策略与评估策略一致
        learning_rate=5e-5,
        per_device_train_batch_size=1,  # 调整 batch size 以适应单张显卡
        per_device_eval_batch_size=1,   # 调整 batch size 以适应单张显卡
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        save_total_limit=2,
        load_best_model_at_end=True,
        fp16=True,  # 使用混合精度训练
        gradient_accumulation_steps=8,  # 累积梯度步数，以模拟更大的 batch size
        dataloader_num_workers=4,
        report_to='none'  # 使用accelerate进行分布式训练，不需要其他报告工具
    )

    # 定义Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['validation'],
        data_collator=data_collator,
    )

    # 使用accelerate加速训练
    trainer = accelerator.prepare(trainer)

    # 开始训练
    trainer.train()

if __name__ == "__main__":
    main()
