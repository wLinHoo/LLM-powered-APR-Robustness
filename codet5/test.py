import os
import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration
from tqdm import tqdm
input_dir = "disturbed"  # 输入文件夹路径
output_dir = "disturbed_p"  # 输出文件夹路径
def process_file(input_path, output_path, model, tokenizer, device):
    # 读取输入文件
    with open(input_path, 'r', encoding='utf-8') as f:
        input_text = f.read()

    # 生成模型输入
    inputs = tokenizer.encode("translate Java to Java: " + input_text, return_tensors="pt", max_length=512, truncation=True).to(device)

    # 生成输出
    outputs = model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)

    # 解码输出
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 保存输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

def process_directory(input_dir, output_dir, model, tokenizer, device):
    # 获取所有 .java 文件路径
    java_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))

    # 使用 tqdm 显示进度条
    for input_path in tqdm(java_files, desc="Processing files"):
        # 构建输出路径
        relative_path = os.path.relpath(input_path, input_dir)
        output_path = os.path.join(output_dir, os.path.dirname(relative_path), os.path.splitext(relative_path)[0] + '-p.java')

        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 处理文件
        process_file(input_path, output_path, model, tokenizer, device)

def main():


    # 检查是否有可用的GPU
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Using GPU: {torch.cuda.get_device_name(torch.cuda.current_device())}")
    else:
        device = torch.device("cpu")
        print("Using CPU")

    # 加载预训练的 CodeT5-base 模型和 tokenizer
    model_name = "codet5-base"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained("checkpoint-base").to(device)

    # 处理目录
    process_directory(input_dir, output_dir, model, tokenizer, device)

if __name__ == "__main__":
    main()
