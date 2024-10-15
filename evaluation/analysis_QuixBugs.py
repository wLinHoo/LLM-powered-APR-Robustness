import os
import re
import pandas as pd
import numpy as np

# 定义要读取的文件列表
files_to_read = ["quixresult/8b_results.txt", "quixresult/70b_results.txt", "quixresult/gemma_results.txt",
                 "quixresult/mistral_results.txt"]
result_file = 'allresultquix.txt'
# 初始化存储数据的结构
data = {
    'bugid': [],
    'disturbance_indices': [],
    'disturbance_level': [],
    'model': [],
    'status': [],
    'categories': []
}


# 定义解析文件名的函数
def parse_filename(filename):
    pattern = r'(.+)-(\d+)-fixed-(.+)\.java'
    match = re.match(pattern, filename)
    if match:
        bugid, disturbance_indices, model = match.groups()
        # 将扰动器索引转换为数组，并计算扰动层级
        disturbance_indices = list(map(int, list(disturbance_indices)))
        disturbance_level = len(disturbance_indices)
        return bugid, disturbance_indices, disturbance_level, model
    return None, None, None, None



# 类别信息
category_info = {
    'Conditional Block': ['BREADTH_FIRST_SEARCH', 'DETECT_CYCLE', 'FIND_FIRST_IN_SORTED', 'GET_FACTORS', 'MERGESORT',
                          'SHORTEST_PATH_LENGTHS'],
    'Expression Fix': ['FIND_FIRST_IN_SORTED', 'FIND_IN_SORTED', 'FLATTEN', 'GET_FACTORS', 'HANOI',
                       'IS_VALID_PARENTHESIZATION', 'KNAPSACK', 'LCS_LENGTH', 'LEVENSHTEIN', 'LIS',
                       'LONGEST_COMMON_SUBSEQUENCE', 'MAX_SUBLIST_SUM', 'MERGESORT', 'NEXT_PERMUTATION', 'RPN_EVAL',
                       'SHORTEST_PATH_LENGTHS', 'SQRT', 'TO_BASE'],
    'Wraps-With': [],
    'Single Line': ['BREADTH_FIRST_SEARCH', 'HANOI', 'KHEAPSORT', 'MAX_SUBLIST_SUM', 'MERGESORT', 'PASCAL',
                    'REVERSE_LINKED_LIST'],
    'Wrong Reference': ['BUCKETSORT', 'FLATTEN', 'KHEAPSORT', 'LEVENSHTEIN', 'MINIMUM_SPANNING_TREE',
                        'SHORTEST_PATH_LENGTHS'],
    'Null-Check': ['DETECT_CYCLE', 'LIS'],
    'Copy/Paste': [],
    'Constant Change': ['SQRT'],
    'Code Moving': ['TO_BASE']
}


# 解析类别
def get_categories(bugid):
    categories = []
    for category, projects in category_info.items():
        if bugid in projects:
            categories.append(category)
    return categories


# 遍历所有文件
file_count = 0
for file_path in files_to_read:
    if os.path.exists(file_path) and file_path.endswith(".txt"):
        file_count += 1
        print(f"Processing file: {file_path}")
        with open(file_path, 'r') as f:
            for line in f:
                # 解析状态
                status = 'Failed' if "Failed" in line else 'Successful' if "Successful" in line else None
                if status is None:
                    continue

                # 从行中解析出文件名
                match = re.search(r'(.+-\d+-fixed-\w+\.java)', line)
                if match:
                    patch_file = match.group(1)
                    bugid, disturbance_indices, disturbance_level, model = parse_filename(patch_file)
                    if bugid and disturbance_indices and model:
                        categories = get_categories(bugid)
                        categories_str = ','.join(categories)
                        # 将信息添加到数据结构中
                        data['bugid'].append(bugid)
                        data['disturbance_indices'].append(tuple(disturbance_indices))  # 转换为元组
                        data['disturbance_level'].append(disturbance_level)
                        data['model'].append(model)
                        data['status'].append(status)
                        data['categories'].append(categories_str)
                    else:
                        print(f"Failed to parse filename: {patch_file}")

print(f"Total files processed: {file_count}")

# 将数据转换为 DataFrame
df = pd.DataFrame(data)

# 确保数据非空
if df.empty:
    raise ValueError("DataFrame is empty. No data was read from the files.")
else:
    print(f"DataFrame successfully created with {len(df)} entries")


# 计算鲁棒性
def calculate_robustness(df):
    # 计算每个项目、扰动器和模型的有效和无效补丁数量
    grouped = df.groupby(['bugid', 'disturbance_level', 'model', 'status']).size().unstack(fill_value=0).reset_index()
    # 确保存在 Successful 和 Failed 列
    if 'Successful' not in grouped.columns:
        grouped['Successful'] = 0
    if 'Failed' not in grouped.columns:
        grouped['Failed'] = 0
    grouped['robustness'] = grouped['Successful'] / (grouped['Successful'] + grouped['Failed'])

    # 计算总鲁棒性
    total_successful = df[df['status'] == 'Successful'].shape[0]
    total_failed = df[df['status'] == 'Failed'].shape[0]
    total_robustness = total_successful / (total_successful + total_failed) if (
                                                                                           total_successful + total_failed) > 0 else np.nan

    return grouped, total_robustness


# 分析扰动层级和鲁棒性之间的关系
def analyze_disturbance_levels(df):
    # 计算每个扰动层级的鲁棒性
    disturbance_grouped = df.groupby(['disturbance_level', 'status']).size().unstack(fill_value=0).reset_index()
    # 确保存在 Successful 和 Failed 列
    if 'Successful' not in disturbance_grouped.columns:
        disturbance_grouped['Successful'] = 0
    if 'Failed' not in disturbance_grouped.columns:
        disturbance_grouped['Failed'] = 0
    disturbance_grouped['robustness'] = disturbance_grouped['Successful'] / (
            disturbance_grouped['Successful'] + disturbance_grouped['Failed'])
    return disturbance_grouped


# 分析单个扰动器的效果
def analyze_single_disturbances(df):
    # 提取单个扰动器的数据
    single_disturbances = df[df['disturbance_level'] == 1]
    # 计算每个单个扰动器的鲁棒性
    single_grouped = single_disturbances.groupby(['disturbance_indices', 'status']).size().unstack(
        fill_value=0).reset_index()
    # 确保存在 Successful 和 Failed 列
    if 'Successful' not in single_grouped.columns:
        single_grouped['Successful'] = 0
    if 'Failed' not in single_grouped.columns:
        single_grouped['Failed'] = 0
    single_grouped['robustness'] = single_grouped['Successful'] / (
                single_grouped['Successful'] + single_grouped['Failed'])
    return single_grouped


# 分析各个大模型的鲁棒性
def analyze_model_robustness(df):
    # 计算每个模型的鲁棒性
    model_grouped = df.groupby(['model', 'status']).size().unstack(fill_value=0).reset_index()
    # 确保存在 Successful 和 Failed 列
    if 'Successful' not in model_grouped.columns:
        model_grouped['Successful'] = 0
    if 'Failed' not in model_grouped.columns:
        model_grouped['Failed'] = 0
    model_grouped['robustness'] = model_grouped['Successful'] / (model_grouped['Successful'] + model_grouped['Failed'])
    return model_grouped


# 分析各个类别的鲁棒性
def analyze_category_robustness(df):
    # 展开每个项目的类别
    expanded_data = []
    for idx, row in df.iterrows():
        categories = row['categories'].split(',')
        for category in categories:
            expanded_data.append({
                'bugid': row['bugid'],
                'disturbance_indices': row['disturbance_indices'],
                'disturbance_level': row['disturbance_level'],
                'model': row['model'],
                'status': row['status'],
                'category': category.strip()
            })

    expanded_df = pd.DataFrame(expanded_data)
    print(expanded_df)
    # 计算每个类别的鲁棒性
    category_grouped = expanded_df.groupby(['category', 'status']).size().unstack(fill_value=0).reset_index()

    # 确保存在 Successful 和 Failed 列
    if 'Successful' not in category_grouped.columns:
        category_grouped['Successful'] = 0
    if 'Failed' not in category_grouped.columns:
        category_grouped['Failed'] = 0

    # 计算鲁棒性
    category_grouped['robustness'] = category_grouped['Successful'] / (
                category_grouped['Successful'] + category_grouped['Failed'])

    # 确保所有类别都包括在内
    all_categories = set(category_info.keys())
    current_categories = set(category_grouped['category'])
    missing_categories = all_categories - current_categories

    missing_df = pd.DataFrame({
        'category': list(missing_categories),
        'Failed': [0] * len(missing_categories),
        'Successful': [0] * len(missing_categories),
        'robustness': [np.nan] * len(missing_categories)
    })

    category_grouped = pd.concat([category_grouped, missing_df], ignore_index=True)

    return category_grouped


# 使用示例 DataFrame 计算鲁棒性
robustness_df, total_robustness = calculate_robustness(df)

# 分析扰动层级和鲁棒性之间的关系
disturbance_levels_df = analyze_disturbance_levels(df)

# 分析单个扰动器的效果
single_disturbances_df = analyze_single_disturbances(df)

# 分析各个大模型的鲁棒性
model_robustness_df = analyze_model_robustness(df)

# 分析各个类别的鲁棒性
category_robustness_df = analyze_category_robustness(df)

# 将结果输出到文件
with open(result_file, 'w') as f:
    f.write("RQ2:\n")
   # f.write(robustness_df.to_csv(sep='\t', index=False))
    f.write(model_robustness_df.to_csv(sep='\t', index=False))
    f.write("\n\nAvg R-score: {:.6f}\n".format(total_robustness))

    f.write("\nRQ3:\n")
    f.write(disturbance_levels_df.to_csv(sep='\t', index=False))

    f.write("\n\nRQ4: \n")
    f.write(single_disturbances_df.to_csv(sep='\t', index=False))

    f.write("\n\nRQ5: \n")
    f.write(category_robustness_df.to_csv(sep='\t', index=False))

print("结果已保存到文件中。")
