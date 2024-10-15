import os
from openai import OpenAI
import concurrent.futures
import re

keylist = [
    ''
]
projects_8b = [
    "BREADTH_FIRST_SEARCH",
    "BUCKETSORT",
    "FIND_FIRST_IN_SORTED",
    "FIND_IN_SORTED",
    "FLATTEN",
    "IS_VALID_PARENTHESIZATION",
    "KNAPSACK",
    "LCS_LENGTH",
    "LONGEST_COMMON_SUBSEQUENCE",
    "MAX_SUBLIST_SUM",
    "MERGESORT",
    "NEXT_PERMUTATION",
    "PASCAL",
    "REVERSE_LINKED_LIST",
    "SHORTEST_PATH_LENGTHS"
]
projects_70b = [
    "FLATTEN",
    "GET_FACTORS",
    "IS_VALID_PARENTHESIZATION",
    "KHEAPSORT",
    "KNAPSACK",
    "LEVENSHTEIN",
    "LIS",
    "LONGEST_COMMON_SUBSEQUENCE",
    "MERGESORT",
    "MINIMUM_SPANNING_TREE",
    "NEXT_PERMUTATION",
    "PASCAL",
    "REVERSE_LINKED_LIST",
    "RPN_EVAL",
    "SHORTEST_PATH_LENGTHS"
]
projects_mistral = [
        "BREADTH_FIRST_SEARCH",
        "BUCKETSORT",
        "FIND_FIRST_IN_SORTED",
        "FIND_IN_SORTED",
        "FLATTEN",
        "IS_VALID_PARENTHESIZATION",
        "KNAPSACK",
        "LEVENSHTEIN",
        "LIS",
        "LONGEST_COMMON_SUBSEQUENCE",
        "MERGESORT",
        "NEXT_PERMUTATION",
        "PASCAL",
        "RPN_EVAL",
        "TO_BASE"
    ]
projects_gemma = [
        "BREADTH_FIRST_SEARCH",
        "BUCKETSORT",
        "FIND_FIRST_IN_SORTED",
        "FIND_IN_SORTED",
        "FLATTEN",
        "KNAPSACK",
        "LCS_LENGTH",
        "LEVENSHTEIN",
        "MERGESORT",
        "REVERSE_LINKED_LIST",
        "RPN_EVAL",
        "TO_BASE",
        "DETECT_CYCLE",
        "HANOI",
        "SQRT",
    ]

model_project_mapping = {
       "8b": projects_8b,
       "70b": projects_70b,
       "mistral": projects_mistral,
       "gemma": projects_gemma
    }

model_name_mapping = {
      "8b": "meta/llama3-8b-instruct",
      "70b": "meta/llama3-70b-instruct",
        "mistral": "mistralai/mistral-large",
       "gemma": "google/codegemma-7b",
    }

base_dir = "D:\py\pub\clean_LLM_repair\QuixBugs\disturbed_new"  # 基础目录
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
    base_output_dir = os.path.join(os.path.dirname(__file__), 'fixedquix', model_key)
    os.makedirs(base_output_dir, exist_ok=True)

    project_id = os.path.basename(project_dir)
    project_output_dir = os.path.join(base_output_dir, project_id)
    os.makedirs(project_output_dir, exist_ok=True)

    for file_name in os.listdir(project_dir):
        if file_name.endswith(".java"):
            file_path = os.path.join(project_dir, file_name)
            output_file_name = f"{file_name[:-5]}-fixed-{model_key}.java"
            output_file_path = os.path.join(project_output_dir, output_file_name)

            # 检查目标文件是否已经存在
            if os.path.exists(output_file_path):
                print(f"File {output_file_path} already exists. Skipping...")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    java_code = file.read()

                fixed_code = fix_code_with_llm(java_code, model_name)
                extracted_code = extract_java_code(fixed_code)

                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(extracted_code)
                    print(f"Fixed code saved to {output_file_path}")
            except Exception as e:
                print(f"Failed to process {file_name}: {e}")
                continue


def main():


    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
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
