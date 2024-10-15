import os
from openai import OpenAI
import concurrent.futures
import re

keylist = [
'yourkeys'
]
output_result = 'fixed_after_LLM'
projects_gemma = ['Closure-7', 'Gson-11', 'JacksonDatabind-1', 'JacksonDatabind-27', 'Closure-109',
                      'JacksonDatabind-99', 'Compress-45', 'Math-95', 'Cli-19', 'Jsoup-70', 'JacksonDatabind-67',
                      'Mockito-29', 'Lang-21', 'Lang-14', 'Math-89']
projects_8b = ['Math-80', 'Closure-7', 'JacksonDatabind-57', 'Math-41', 'Jsoup-85', 'JacksonDatabind-1',
                   'Mockito-29', 'Lang-14', 'JacksonCore-5', 'Compress-45', 'Math-95', 'Lang-21', 'Jsoup-48',
                   'Closure-109', 'Compress-46']
projects_70b = ['Closure-126', 'Lang-45', 'Time-15', 'Mockito-38', 'Lang-21', 'Jsoup-70', 'Closure-44', 'Math-41',
                    'Mockito-34', 'Math-59', 'Math-82', 'Math-11', 'Lang-14', 'Lang-12', 'Closure-109']
projects_mistral = ['Lang-33', 'Mockito-38', 'JacksonCore-5', 'Lang-59', 'Cli-8', 'Lang-12', 'Lang-21',
                        'Mockito-34', 'Jsoup-45', 'JacksonDatabind-1', 'Compress-46', 'Cli-28', 'Cli-17', 'Codec-6',
                        'Lang-14']
model_project_mapping = {
        "gemma": projects_gemma,
        "8b": projects_8b,
        "70b": projects_70b,
        "mistral": projects_mistral
    }
model_name_mapping = {
        "gemma": "google/codegemma-7b",
        "8b": "meta/llama3-8b-instruct",
        "70b": "meta/llama3-70b-instruct",
        "mistral": "mistralai/mistral-large"
    }
base_dir = "clean_LLM_repair/Dataset/disturbed_new"  # 基础目录
workers = 20


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

def process_project(project_dir, model_key, model_name):
    global output_result
    base_output_dir = os.path.join(os.path.dirname(__file__), output_result, model_key)
    os.makedirs(base_output_dir, exist_ok=True)

    project_id = os.path.basename(project_dir)
    project_output_dir = os.path.join(base_output_dir, project_id)
    os.makedirs(project_output_dir, exist_ok=True)

    for file_name in os.listdir(project_dir):
        if file_name.endswith(".java"):
            file_path = os.path.join(project_dir, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    java_code = file.read()

                fixed_code = fix_code_with_llm(java_code, model_name)
                extracted_code = extract_java_code(fixed_code)

                output_file_name = f"{file_name[:-5]}-fixed-{model_key}.java"
                output_file_path = os.path.join(project_output_dir, output_file_name)
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(extracted_code)
                    print(f"Fixed code saved to {output_file_path}")
            except Exception as e:
                print(f"Failed to process {file_name}: {e}")
                continue


def main():

    global workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for model_key, projects in model_project_mapping.items():
            model_name = model_name_mapping[model_key]
            for project in projects:
                project_dir = os.path.join(base_dir, project)
                if os.path.isdir(project_dir):
                    print(f"Processing {project} with model {model_name}")
                    futures.append(executor.submit(process_project, project_dir, model_key, model_name))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception occurred: {e}")


if __name__ == "__main__":
    main()
