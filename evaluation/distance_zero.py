import json
# 指定 JSONL 文件路径
file_path = 'distances.jsonl'


def process_jsonl_file(file_path):
    total_count = 0
    positive_count = 0
    a = 0
    # 打开 JSONL 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 解析每一行 JSON 数据
            data = json.loads(line)

            # 获取 disturbed 和 disturbed_p 的值
            disturbed = data.get('disturbed', 0)
            disturbed_p = data.get('disturbed_p', 0)
            # 计算差值
            difference = disturbed_p - disturbed

            # 如果差值大于 0，则计数加 1
            if difference < 0:
                positive_count += 1
            if disturbed_p == 0:
                a += 1

            # 总计数加 1
            total_count += 1

    # 计算大于 0 的百分比
    percentage_positive = (positive_count / total_count) * 100 if total_count > 0 else 0

    print(f"Total JSON entries: {total_count}")
    print(f"Count of the disturbance distance reduced to 0: {a}")
    print(f"Percentage of disturbance distance reduced to 0:{((a / total_count)* 100 if total_count > 0 else 0):.2f}%")
    print(f"Count of positive differences: {positive_count}")
    print(f"Percentage of positive differences: {percentage_positive:.2f}%")



# 调用函数
process_jsonl_file(file_path)
