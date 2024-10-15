import os
import json
from typing import List, Dict


directory = r"D:\py\pub\clean_LLM_repair\QuixBugs\java_programs"
disturbed_dir = 'D:\py\pub\clean_LLM_repair\QuixBugs\disturbed_new'
disturbed_p_dir = 'D:\py\pub\clean_LLM_repair\QuixBugs\disturbed_new'
output_file = 'distances1.jsonl'

def word_level_edit_distance(a: List[str], b: List[str]) -> int:
    max_dis = max(len(a), len(b))
    distances = [[max_dis for j in range(len(b)+1)] for i in range(len(a)+1)]
    for i in range(len(a)+1):
        distances[i][0] = i
    for j in range(len(b)+1):
        distances[0][j] = j

    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            distances[i][j] = min(distances[i-1][j] + 1,
                                  distances[i][j-1] + 1,
                                  distances[i-1][j-1] + cost)
    return distances[-1][-1]

def get_project_version(filename: str) -> (str, int, bool):
    parts = filename.split('-')
    if len(parts) == 3:
        project_name = f"{parts[0]}-{parts[1]}"
        version = int(parts[2].replace('.java', ''))
        is_p = False
    elif len(parts) == 4:
        project_name = f"{parts[0]}-{parts[1]}"
        version = int(parts[2])
        is_p = parts[3].replace('.java', '') == 'p'
    else:
        project_name = parts[0]
        version = int(parts[1].replace('.java', ''))
        is_p = False
    return project_name, version, is_p
def get_project_version_quix(filename: str) -> (str, int):
    parts = filename.split('-')
    if len(parts) == 2:
        project_name = parts[0]
        version = int(parts[1].replace('.java', ''))
    else:
        raise ValueError("Invalid filename format.")
    return project_name, version

def calculate_edit_distance_for_project_versions(base_dir: str, cleaned_data: Dict[str, Dict[str, str]], distances: Dict[str, Dict[int, Dict[str, int]]], key: str):
    print(f"Processing directory: {base_dir}")
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".java"):
                project_name, version= get_project_version_quix(file)
                is_p = 0
                if f'{project_name}.java' in cleaned_data:
                    original_code = cleaned_data[f'{project_name}.java']['buggy']
                    with open(os.path.join(root, file), 'r') as f:
                        disturbed_code = f.read()
                    original_words = original_code.split()
                    disturbed_words = disturbed_code.split()
                    edit_distance = word_level_edit_distance(original_words, disturbed_words)
                    if project_name not in distances:
                        distances[project_name] = {}
                    if version not in distances[project_name]:
                        distances[project_name][version] = {}
                    if is_p:
                        distances[project_name][version]['disturbed_p'] = edit_distance
                    else:
                        distances[project_name][version]['disturbed'] = edit_distance
                else:
                    print(f"Original code for project {project_name} not found in cleaned_data.")

def save_distances_to_jsonl(distances: Dict[str, Dict[int, Dict[str, int]]], output_file: str):
    with open(output_file, 'w') as f:
        for project_name, versions in distances.items():
            for version, distance_data in versions.items():
                record = {
                    'id': f'{project_name}-{version}',
                    'disturbed': distance_data.get('disturbed', None),
                    'disturbed_p': distance_data.get('disturbed_p', None)
                }
                f.write(json.dumps(record) + '\n')

# 假设cleaned_data已经被初始化
def clean_parse_d4j():
    with open("single_function_repair1.json", "r") as f:
        result = json.load(f)
    cleaned_result = {}
    for k, v in result.items():
        lines = v['buggy'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        lines = v['fix'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"]["fix"] = "\n".join([line[leading_white_space:] for line in lines])
    return cleaned_result


def clean_parse_quix(directory):
    cleaned_result = {}

    # 遍历指定目录下的所有文件
    for filename in os.listdir(directory):
        if filename.endswith(".java"):
            filepath = os.path.join(directory, filename)

            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

                # 假设文件中的内容就是 buggy 代码
                buggy_code = content

                # 移除首行的前导空白字符
                lines = buggy_code.splitlines()
                leading_white_space = len(lines[0]) - len(lines[0].lstrip())
                cleaned_buggy_code = "\n".join([line[leading_white_space:] for line in lines])

                # 创建字典条目
                key = filename
                cleaned_result[key] = {
                    "buggy": cleaned_buggy_code,
                    "fix": ""
                }

    return cleaned_result


def calculate_averages(jsonl_file_path):
    total_disturbed = 0
    total_disturbed_p = 0
    count = 0

    with open(jsonl_file_path, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            total_disturbed += data['disturbed']
            total_disturbed_p += data['disturbed_p']
            count += 1

    average_disturbed = total_disturbed / count if count > 0 else 0
    average_disturbed_p = total_disturbed_p / count if count > 0 else 0

    return average_disturbed, average_disturbed_p

cleaned_data = clean_parse_quix(directory)


distances = {}
calculate_edit_distance_for_project_versions(disturbed_dir, cleaned_data, distances, 'disturbed')
calculate_edit_distance_for_project_versions(disturbed_p_dir, cleaned_data, distances, 'disturbed_p')


save_distances_to_jsonl(distances, output_file)

print(f"Distances saved to {output_file}")
# 使用方法
jsonl_file_path = output_file  # 请替换为你的文件路径
average_disturbed, average_disturbed_p = calculate_averages(jsonl_file_path)
print(f"Average disturbed: {average_disturbed}")
print(f"Average disturbed_p: {average_disturbed_p}")
