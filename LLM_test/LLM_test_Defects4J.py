import json
import os
from openai import OpenAI
import json

input_file = "clean_LLM_repair/Dataset/single_function_repair.json"
keylist = [
    'your_keys'
]
llm_models = ["mistralai/mistral-large"]
output_dir = "fixed_code"

def clean_parse_d4j():
    global input_file
    with open(input_file, "r") as f:
        result = json.load(f)

    cleaned_result = {}
    for k, v in result.items():
        # 处理buggy部分的代码
        lines = v['buggy'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"] = {
            "buggy": "\n".join([line[leading_white_space:] for line in lines])
        }

        # 处理fix部分的代码
        if 'fix' in v:  # 确保fix键存在
            lines = v['fix'].splitlines()
            leading_white_space = len(lines[0]) - len(lines[0].lstrip())
            cleaned_result[k + ".java"]["fix"] = "\n".join([line[leading_white_space:] for line in lines])

    return cleaned_result



index = 0  # 初始索引
def get_next_key():
    global index
    key = keylist[index]
    index = (index + 1) % len(keylist)  # 循环到下一个key，若到达末尾则回到开头
    return key

def fix_code_with_llm(java_code, model_name):
    prompt = f"""
    The following Java code contains a bug. Your task is to fix the bug and provide the corrected code only. Do not include any other text in your response.
    Buggy code:
    {java_code}
    Fixed code:
    """

    current_key = get_next_key()

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=current_key
    )

    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        top_p=0.8,
        max_tokens=1024,
        stream=True
    )

    fixed_code = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            fixed_code += chunk.choices[0].delta.content

    return fixed_code


def main():
    global llm_models
    cleaned_data = clean_parse_d4j()

    for model_name in llm_models:
        # 创建保存修复代码的文件夹
        global output_dir
        os.makedirs(output_dir, exist_ok=True)

        for file_key in cleaned_data:
            try:
                # 获取buggy代码
                java_code = cleaned_data[file_key]['buggy']

                # 修复代码
                fixed_code = fix_code_with_llm(java_code, model_name)

                # 提取文件名前缀
                file_prefix = file_key.split('.')[0]

                # 保存修复后的代码到指定文件
                output_file_path = os.path.join(output_dir, f"{file_prefix}-{model_name.replace('/', '_')}.java")
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(fixed_code)
                    print(f"Fixed code saved to {output_file_path}")
            except:
                continue

if __name__ == "__main__":
    main()
