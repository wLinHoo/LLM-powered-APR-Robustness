import subprocess
from itertools import combinations
import random
import os

input_directory = "./java_programs"  # 输入文件夹路径
java_class_path = "javaparser-core-3.25.8.jar"
output_directory = f"disturbed"
def run_java_program(java_code, perturbation_sequence):
    global java_class_path
    perturbation_string = ",".join(map(str, perturbation_sequence))
    command = ['java', '-cp', java_class_path, 'Main', java_code, perturbation_string]

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            return extract_code(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Failed to run Java program:", e)


def extract_code(output):
    start_marker = "---START OF CODE---"
    end_marker = "---END OF CODE---"
    start_idx = output.find(start_marker) + len(start_marker)
    end_idx = output.find(end_marker)
    if start_idx != -1 and end_idx != -1:
        return output[start_idx:end_idx].strip()
    return "No code block found."


def is_valid_transformation(original_code, transformed_code):
    return original_code.replace(" ", "").replace("\n", "") != transformed_code.replace(" ", "").replace("\n", "")


def generate_valid_perturbations(java_code):
    possible_perturbations = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 1 to 9
    valid_perturbations = []

    for perturbation in possible_perturbations:
        transformed_code = run_java_program(java_code, [perturbation])
        if transformed_code and is_valid_transformation(java_code, transformed_code):
            valid_perturbations.append(perturbation)

    return valid_perturbations


def generate_and_filter_combinations(valid_perturbations):
    all_combinations = []
    n = len(valid_perturbations)
    for r in range(1, n + 1):
        comb = list(combinations(valid_perturbations, r))
        if len(comb) > 20:
            comb = random.sample(comb, 20)  # 如果组合数大于20，随机抽取20个
        all_combinations.extend(comb)
    return all_combinations


def save_code_to_file(base_name, perturbation_sequence, code):
    global output_directory
    directory = output_directory + '/' + base_name
    if not os.path.exists(directory):
        os.makedirs(directory)  # 如果目录不存在则创建

    sequence_str = ''.join(map(str, perturbation_sequence))  # 将序列转换为字符串
    file_name = f"{base_name}-{sequence_str}.java"  # 生成文件名
    file_path = os.path.join(directory, file_name)  # 完整的文件路径

    try:
        with open(file_path, 'w') as file:
            file.write(code)  # 写入处理后的代码
        print(f"Code saved to {file_path}")
    except OSError as e:
        print(f"Failed to save file due to an OS error: {e}")

if __name__ == "__main__":


    # 遍历输入文件夹中的所有 .java 文件
    for filename in os.listdir(input_directory):
        if filename.endswith(".java"):
            base_name = os.path.splitext(filename)[0]
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r') as file:
                original_code = file.read()  # 读取原始代码

            valid_perturbations = generate_valid_perturbations(original_code)  # 生成有效的变换序列
            all_combinations = generate_and_filter_combinations(valid_perturbations)  # 生成并过滤变换组合

            # 处理每个变换组合
            for perturbation_sequence in all_combinations:
                transformed_code = run_java_program(original_code, perturbation_sequence)  # 运行Java程序进行代码变换
                if transformed_code and is_valid_transformation(original_code, transformed_code):
                    save_code_to_file(base_name, perturbation_sequence, transformed_code)  # 保存变换后的代码
