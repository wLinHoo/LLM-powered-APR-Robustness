import os
import re

source_folder = 'fixed_code_mistral-large'
target_folder = 'fixed_code_mistral-large-t'

def extract_java_code(text):
    # 正则表达式匹配包含在 ```java 和 ``` 之间的文本
    pattern = re.compile(r"```java(.*?)```", re.DOTALL)
    matches = pattern.findall(text)
    if matches:
        return matches[0].strip()  # 提取第一个匹配的Java代码部分并去除首尾空格
    return None

def process_directory(source_folder, target_folder):
    # 确保目标文件夹存在
    os.makedirs(target_folder, exist_ok=True)

    # 遍历源文件夹中的所有文件
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.java'):  # 确认文件扩展名
            source_file_path = os.path.join(source_folder, file_name)
            target_file_path = os.path.join(target_folder, file_name)

            # 读取文件内容
            with open(source_file_path, 'r',encoding='utf8') as file:
                content = file.read()

            # 提取Java代码
            java_code = extract_java_code(content)
            if java_code:
                # 将提取的Java代码保存到新文件中
                with open(target_file_path, 'w') as file:
                    file.write(java_code)
                print(f"Java code from {file_name} saved to {target_file_path}")
            else:
                print(f"No Java code found in {file_name}")
# 调用函数处理目录
process_directory(source_folder, target_folder)
