import os
import re
import pandas as pd
import numpy as np

root_directory = "fixresultnew"
result_file = 'result.txt'

# 初始化存储数据的结构
data = {
    'bugid': [],
    'disturbance_indices': [],
    'disturbance_level': [],
    'model': [],
    'status': []
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

# 遍历所有子目录和文件

file_count = 0
for subdir, _, files in os.walk(root_directory):
    for file in files:
        if file.endswith(".txt"):  # 假设记录信息的文件是以 .txt 结尾
            file_count += 1
            file_path = os.path.join(subdir, file)
            print(f"Processing file: {file_path}")
            with open(file_path, 'r') as f:
                for line in f:
                    # 解析状态
                    if "has invalid patch" in line:
                        status = 'invalid'
                    elif "has valid patch" in line:
                        status = 'valid'
                    else:
                        continue

                    # 从行中解析出文件名
                    match = re.search(r'has (valid|invalid) patch: (.+)', line)
                    if match:
                        patch_file = match.group(2)
                        bugid, disturbance_indices, disturbance_level, model = parse_filename(
                            os.path.basename(patch_file))
                        if bugid and disturbance_indices and model:
                            # 将信息添加到数据结构中
                            data['bugid'].append(bugid)
                            data['disturbance_indices'].append(tuple(disturbance_indices))  # 转换为元组
                            data['disturbance_level'].append(disturbance_level)
                            data['model'].append(model)
                            data['status'].append(status)
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
    # 确保存在 valid 和 invalid 列
    if 'valid' not in grouped.columns:
        grouped['valid'] = 0
    if 'invalid' not in grouped.columns:
        grouped['invalid'] = 0
    grouped['robustness'] = grouped['valid'] / (grouped['valid'] + grouped['invalid'])

    # 计算总鲁棒性
    total_valid = df[df['status'] == 'valid'].shape[0]
    total_invalid = df[df['status'] == 'invalid'].shape[0]
    total_robustness = total_valid / (total_valid + total_invalid) if (total_valid + total_invalid) > 0 else np.nan

    return grouped, total_robustness

# 分析扰动层级和鲁棒性之间的关系
def analyze_disturbance_levels(df):
    # 计算每个扰动层级的鲁棒性
    disturbance_grouped = df.groupby(['disturbance_level', 'status']).size().unstack(fill_value=0).reset_index()
    # 确保存在 valid 和 invalid 列
    if 'valid' not in disturbance_grouped.columns:
        disturbance_grouped['valid'] = 0
    if 'invalid' not in disturbance_grouped.columns:
        disturbance_grouped['invalid'] = 0
    disturbance_grouped['robustness'] = disturbance_grouped['valid'] / (
            disturbance_grouped['valid'] + disturbance_grouped['invalid'])
    return disturbance_grouped

# 分析单个扰动器的效果
def analyze_single_disturbances(df):
    # 提取单个扰动器的数据
    single_disturbances = df[df['disturbance_level'] == 1]
    # 计算每个单个扰动器的鲁棒性
    single_grouped = single_disturbances.groupby(['disturbance_indices', 'status']).size().unstack(
        fill_value=0).reset_index()
    # 确保存在 valid 和 invalid 列
    if 'valid' not in single_grouped.columns:
        single_grouped['valid'] = 0
    if 'invalid' not in single_grouped.columns:
        single_grouped['invalid'] = 0
    single_grouped['robustness'] = single_grouped['valid'] / (single_grouped['valid'] + single_grouped['invalid'])
    return single_grouped

# 分析各个大模型的鲁棒性
def analyze_model_robustness(df):
    # 计算每个模型的鲁棒性
    model_grouped = df.groupby(['model', 'status']).size().unstack(fill_value=0).reset_index()
    # 确保存在 valid 和 invalid 列
    if 'valid' not in model_grouped.columns:
        model_grouped['valid'] = 0
    if 'invalid' not in model_grouped.columns:
        model_grouped['invalid'] = 0
    model_grouped['robustness'] = model_grouped['valid'] / (model_grouped['valid'] + model_grouped['invalid'])
    return model_grouped

# 定义表格数据
data_categories = {
    'Mistral': {
        'projects': ['Lang-33', 'Mockito-38', 'JacksonCore-5', 'Lang-59', 'Cli-8', 'Lang-12', 'Lang-21', 'Mockito-34',
                     'Jsoup-45', 'JacksonDatabind-1', 'Compress-46', 'Cli-28', 'Cli-17', 'Codec-6', 'Lang-14'],
        'Conditional Block': {
            'condBlockExcAdd': ['Lang-12'],
            'condBlockAdd': ['Codec-6'],
            'condBlockRetAdd': ['Cli-28', 'JacksonDatabind-1'],
            'condBlockRem': ['Cli-17'],
            'condBlockOthersAdd': ['0'],
            'blockRemove': ['Cli-17']
        },
        'Missing Null-Check': {
            'missNullCheckN': ['Lang-12'],
            'missNullCheckP': ['Lang-33', 'Mockito-38']
        },
        'Wraps-with/Unwraps-from': {
            'wrapsIfElse': ['Lang-12', 'Lang-33', 'Mockito-38'],
            'wrapsIf': ['Lang-14'],
            'wrapsElse': ['0'],
            'wrapsTryCatch': ['0'],
            'wrapsMethod': ['0'],
            'wrapsLoop': ['0'],
            'unwrapIfElse': ['0'],
            'unwrapMethod': ['0'],
            'unwrapTryCatch': ['0']
        },
        'Constant Change': {
            'constChange': ['Lang-21']
        },
        'Expression Fix': {
            'expLogicMod': ['Lang-21', 'Compress-46', 'Jsoup-45'],
            'expArithMod': ['Cli-8', 'JacksonCore-5'],
            'expLogicExpand': ['Mockito-34'],
            'expLogicReduce': ['0']
        },
        'Single Line': {
            'singleLine': ['Lang-21', 'Lang-33', 'Lang-59', 'Mockito-34', 'Mockito-38']
        },
        'Wrong Reference': {
            'wrongVarRef': ['Lang-21', 'Lang-59'],
            'wrongComp': ['Lang-59'],
            'wrongMethodRef': ['0']
        },
        'Copy/Paste': {
            'copyPaste': ['0']
        },
        'Code Moving': {
            'codeMove': ['0']
        }
    },
    '7b': {
        'projects': ['Closure-7', 'Gson-11', 'JacksonDatabind-1', 'JacksonDatabind-27', 'Closure-109', 'JacksonDatabind-99',
                     'Compress-45', 'Math-95', 'Cli-19', 'Jsoup-70', 'JacksonDatabind-67', 'Mockito-29', 'Lang-21', 'Lang-14', 'Math-89'],
        'Conditional Block': {
            'condBlockRetAdd': ['Closure-7', 'Closure-109', 'JacksonDatabind-1'],
            'condBlockAdd': ['Compress-45', 'Gson-11', 'JacksonDatabind-67', 'Jsoup-70'],
            'condBlockExcAdd': ['0'],
            'condBlockRem': ['0'],
            'condBlockOthersAdd': ['JacksonDatabind-67'],
            'blockRemove': ['0']
        },
        'Expression Fix': {
            'expLogicReduce': ['Closure-7'],
            'expLogicMod': ['JacksonDatabind-27'],
            'expArithMod': ['JacksonDatabind-99'],
            'expLogicExpand': ['0']
        },
        'Wrong Reference': {
            'wrongComp': ['Closure-7', 'Closure-109'],
            'wrongMethodRef': ['Closure-109'],
            'wrongVarRef': ['Lang-21']
        },
        'Wraps-with/Unwraps-from': {
            'wrapsIfElse': ['Math-89'],
            'wrapsIf': ['Lang-14', 'Math-95'],
            'wrapsElse': ['0'],
            'wrapsTryCatch': ['0'],
            'wrapsMethod': ['0'],
            'wrapsLoop': ['0'],
            'unwrapIfElse': ['0'],
            'unwrapMethod': ['0'],
            'unwrapTryCatch': ['0']
        },
        'Constant Change': {
            'constChange': ['Lang-21']
        },
        'Single Line': {
            'singleLine': ['Lang-21', 'Mockito-29']
        },
        'Missing Null-Check': {
            'missNullCheckP': ['Mockito-29'],
            'missNullCheckN': ['0']
        },
        'Copy/Paste': {
            'copyPaste': ['0']
        },
        'Code Moving': {
            'codeMove': ['Cli-19', 'Jsoup-70']
        }
    },
    '8b': {
        'projects': ['Math-80', 'Closure-7', 'JacksonDatabind-57', 'Math-41', 'Jsoup-85', 'JacksonDatabind-1', 'Mockito-29',
                     'Lang-14', 'JacksonCore-5', 'Compress-45', 'Math-95', 'Lang-21', 'Jsoup-48', 'Closure-109', 'Compress-46'],
        'Conditional Block': {
            'condBlockRetAdd': ['Closure-7', 'Closure-109', 'JacksonDatabind-1'],
            'condBlockAdd': ['Compress-45', 'Jsoup-48'],
            'condBlockExcAdd': ['0'],
            'condBlockRem': ['0'],
            'condBlockOthersAdd': ['0'],
            'blockRemove': ['0']
        },
        'Expression Fix': {
            'expLogicReduce': ['Closure-7'],
            'expLogicMod': ['Lang-21', 'Compress-46', 'Jsoup-48', 'Jsoup-85'],
            'expArithMod': ['Math-80', 'JacksonCore-5', 'JacksonDatabind-57'],
            'expLogicExpand': ['0']
        },
        'Wrong Reference': {
            'wrongComp': ['Closure-7', 'Closure-109'],
            'wrongMethodRef': ['Closure-109'],
            'wrongVarRef': ['Lang-21', 'Math-41']
        },
        'Wraps-with/Unwraps-from': {
            'wrapsIfElse': ['Closure-109', 'Mockito-29'],
            'wrapsIf': ['Lang-14', 'Math-95'],
            'wrapsElse': ['0'],
            'wrapsTryCatch': ['0'],
            'wrapsMethod': ['0'],
            'wrapsLoop': ['0'],
            'unwrapIfElse': ['0'],
            'unwrapMethod': ['0'],
            'unwrapTryCatch': ['0']
        },
        'Constant Change': {
            'constChange': ['Lang-21']
        },
        'Single Line': {
            'singleLine': ['Lang-21', 'Math-41', 'Math-80', 'Mockito-29']
        },
        'Missing Null-Check': {
            'missNullCheckP': ['Mockito-29'],
            'missNullCheckN': ['0']
        },
        'Copy/Paste': {
            'copyPaste': ['0']
        },
        'Code Moving': {
            'codeMove': ['0']
        }
    },
    '70b': {
        'projects': ['Closure-126', 'Lang-45', 'Time-15', 'Mockito-38', 'Lang-21', 'Jsoup-70', 'Closure-44', 'Math-41',
                     'Mockito-34', 'Math-59', 'Math-82', 'Math-11', 'Lang-14', 'Lang-12', 'Closure-109'],
        'Conditional Block': {
            'condBlockOthersAdd': ['Closure-44', 'Lang-45'],
            'condBlockRetAdd': ['Closure-109', 'Jsoup-70'],
            'condBlockRem': ['Closure-126'],
            'condBlockExcAdd': ['Lang-12', 'Time-15'],
            'condBlockAdd': ['0'],
            'blockRemove': ['0']
        },
        'Wraps-with/Unwraps-from': {
            'wrapsIfElse': ['Closure-109', 'Lang-12', 'Mockito-38'],
            'wrapsIf': ['Lang-14'],
            'wrapsElse': ['0'],
            'wrapsTryCatch': ['0'],
            'wrapsMethod': ['0'],
            'wrapsLoop': ['0'],
            'unwrapIfElse': ['0'],
            'unwrapMethod': ['0'],
            'unwrapTryCatch': ['0']
        },
        'Wrong Reference': {
            'wrongComp': ['Closure-109'],
            'wrongMethodRef': ['Closure-109'],
            'wrongVarRef': ['Lang-21', 'Math-41', 'Math-59']
        },
        'Missing Null-Check': {
            'missNullCheckN': ['Lang-12'],
            'missNullCheckP': ['Mockito-38']
        },
        'Constant Change': {
            'constChange': ['Lang-21']
        },
        'Expression Fix': {
            'expLogicMod': ['Lang-21', 'Math-82'],
            'expArithMod': ['Math-11'],
            'expLogicExpand': ['Mockito-34'],
            'expLogicReduce': ['0']
        },
        'Single Line': {
            'singleLine': ['Lang-21', 'Math-11', 'Math-41', 'Math-59', 'Math-82', 'Mockito-34', 'Mockito-38']
        },
        'Copy/Paste': {
            'copyPaste': ['0']
        },
        'Code Moving': {
            'codeMove': ['Jsoup-70']
        }
    }
}
# 定义函数计算每个大类和小类的鲁棒性
def calculate_category_robustness(data_categories, df):
    results = []
    for category, details in data_categories.items():
        projects = details['projects']
        category_valid_count = df[df['bugid'].isin(projects) & (df['status'] == 'valid')]['bugid'].count()
        category_invalid_count = df[df['bugid'].isin(projects) & (df['status'] == 'invalid')]['bugid'].count()
        category_robustness = category_valid_count / (category_valid_count + category_invalid_count) if (
                                                                                                                    category_valid_count + category_invalid_count) > 0 else np.nan

        for subcategory, subprojects in details.items():
            if subcategory == 'projects':
                continue
            subcategory_valid_count = 0
            subcategory_invalid_count = 0
            for subsubcategory, bugs in subprojects.items():
                valid_count = df[df['bugid'].isin(bugs) & (df['status'] == 'valid')]['bugid'].count()
                invalid_count = df[df['bugid'].isin(bugs) & (df['status'] == 'invalid')]['bugid'].count()
                robustness = valid_count / (valid_count + invalid_count) if (
                                                                                        valid_count + invalid_count) > 0 else np.nan
                results.append([category, subcategory, subsubcategory, valid_count, invalid_count, robustness])
                subcategory_valid_count += valid_count
                subcategory_invalid_count += invalid_count

            subcategory_robustness = subcategory_valid_count / (
                        subcategory_valid_count + subcategory_invalid_count) if (
                                                                                            subcategory_valid_count + subcategory_invalid_count) > 0 else np.nan
            results.append([category, subcategory, 'Total', subcategory_valid_count, subcategory_invalid_count,
                            subcategory_robustness])

        results.append([category, 'Total', 'Total', category_valid_count, category_invalid_count, category_robustness])

    return pd.DataFrame(results,
                        columns=['Category', 'Subcategory', 'Subsubcategory', 'Valid', 'Invalid', 'Robustness'])

# 使用示例 DataFrame 计算鲁棒性
robustness_df, total_robustness = calculate_robustness(df)

# 分析扰动层级和鲁棒性之间的关系
disturbance_levels_df = analyze_disturbance_levels(df)

# 分析单个扰动器的效果
single_disturbances_df = analyze_single_disturbances(df)

# 分析各个大模型的鲁棒性
model_robustness_df = analyze_model_robustness(df)

# 计算大类和小类的鲁棒性
category_robustness_df = calculate_category_robustness(data_categories, df)

# 汇总所有模型的数据
total_data = category_robustness_df.groupby(['Subcategory', 'Subsubcategory']).sum().reset_index()

# 计算总鲁棒性
total_data['Robustness'] = total_data['Valid'] / (total_data['Valid'] + total_data['Invalid'])

# 更新Category列为'Total'
total_data['Category'] = 'Total'

# 将总结果追加到 category_robustness_df
final_df = pd.concat([category_robustness_df, total_data], ignore_index=True)

# 将结果输出到文件
with open(result_file, 'w') as f:
    f.write("RQ2\n")
    #f.write(robustness_df.to_csv(sep='\t', index=False))
    f.write("\n\nAvg R-score: {:.6f}\n".format(total_robustness))

    f.write(model_robustness_df.to_csv(sep='\t', index=False))
    f.write("\nRQ3\n")
    f.write(disturbance_levels_df.to_csv(sep='\t', index=False))

    f.write("\n\nRQ4\n")
    f.write(single_disturbances_df.to_csv(sep='\t', index=False))

    f.write("\n\nRQ5\n")
    f.write(final_df.to_csv(sep='\t', index=False))

print("结果已保存到文件中。")
