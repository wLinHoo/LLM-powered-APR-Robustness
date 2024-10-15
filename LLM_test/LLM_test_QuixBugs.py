import os
from openai import OpenAI
import concurrent.futures
import re

keylist = [
    'your_key'
]
buggy_dir = "java_programs"
fixed_dir = "JavaFixed"
models = {
       "gemma": "google/codegemma-7b",
        "8b": "meta/llama3-8b-instruct",
        "70b": "meta/llama3-70b-instruct",
        "mistral": "mistralai/mistral-large"
    }
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


def extract_java_code(text):
    # 正则表达式匹配包含在 ```java 和 ``` 之间的文本
    pattern = re.compile(r"```java(.*?)```", re.DOTALL)
    matches = pattern.findall(text)
    if matches:
        return matches[0].strip()  # 提取第一个匹配的Java代码部分并去除首尾空格
    return text  # 如果没有匹配，返回原始文本


def process_file(file_path, model_name, model_suffix, output_dir):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            java_code = file.read()

        fixed_code = fix_code_with_llm(java_code, model_name)
        extracted_code = extract_java_code(fixed_code)

        file_name = os.path.basename(file_path)
        output_file_name = f"{os.path.splitext(file_name)[0]}.java"
        output_file_path = os.path.join(output_dir, output_file_name)
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(extracted_code)
            print(f"Fixed code saved to {output_file_path}")
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")


def main():



    if not os.path.exists(fixed_dir):
        os.makedirs(fixed_dir)

    java_files = [os.path.join(buggy_dir, file_name) for file_name in os.listdir(buggy_dir) if
                  file_name.endswith(".java")]

    # 确保每个模型有40个文件来处理
    java_files_chunks = [java_files[i:i + 40] for i in range(0, len(java_files), 40)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, (suffix, model_name) in enumerate(models.items()):
            if i < len(java_files_chunks):
                chunk = java_files_chunks[i]
                output_subdir = os.path.join(fixed_dir, suffix)
                futures.extend(
                    [executor.submit(process_file, file_path, model_name, suffix, output_subdir) for file_path in
                     chunk])

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception occurred: {e}")


if __name__ == "__main__":
    main()
