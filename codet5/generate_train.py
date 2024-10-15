import os
import json

# 定义文件夹路径和 JSON 文件路径
disturb_fail_dir = "disturbed_fail"
repair_json_path = "single_function_repair.json"
output_json_path = "generate_data.json"

# 加载 repair.json 文件
with open(repair_json_path, "r") as f:
    repair_data = json.load(f)

# 初始化数据列表
data_list = []

# 遍历 disturb_fail 文件夹中的子文件夹
for bugid in os.listdir(disturb_fail_dir):
    subfolder_path = os.path.join(disturb_fail_dir, bugid)
    if os.path.isdir(subfolder_path):
        # 遍历子文件夹中的 .java 文件
        for java_file in os.listdir(subfolder_path):
            if java_file.endswith(".java"):
                java_file_path = os.path.join(subfolder_path, java_file)
                with open(java_file_path, "r") as f:
                    input_text = f.read()

                # 从 repair_data 中获取 buggy 版本
                buggy_version = repair_data.get(bugid, {}).get("buggy", "")

                # 获取文件名去除 .java 后缀
                file_id = os.path.splitext(java_file)[0]

                # 构造数据条目
                data_entry = {
                    "input_text": input_text,
                    "target_text": buggy_version,
                    "id": f"{file_id}"
                }

                # 添加到数据列表
                data_list.append(data_entry)

# 构造最终的 JSON 结构
final_data = {"data": data_list}

# 保存为 JSON 文件

with open(output_json_path, "w") as f:
    json.dump(final_data, f, indent=4, ensure_ascii=False)

print(f"数据已生成并保存到 {output_json_path}")
