import os
import json

distances_file = 'distancesl.jsonl'
fixresultp_dir = 'D:\\py\\pub\\fixresultpl'

def load_distances(jsonl_file):
    distances = {}
    with open(jsonl_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            distances[data['id']] = {
                'disturbed': data['disturbed'],
                'disturbed_p': data['disturbed_p']
            }
    print(f"Loaded {len(distances)} distances from {jsonl_file}")
    return distances

def calculate_averages_for_valid_files(base_dir, distances):
    total_disturbed = 0
    total_disturbed_p = 0
    count_disturbed = 0
    count_disturbed_p = 0

    for model in ['8b', '70b']:
        model_dir = os.path.join(base_dir, model)
        for root, _, files in os.walk(model_dir):
            for file in files:
                if file.startswith('valid'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        for line in f:
                            if 'has valid patch' in line:
                                parts = line.split('/')
                                file_name = parts[-1].replace('-fixed-8b.java', '').replace('-fixed-70b.java', '')
                                file_id = file_name.replace('-p', '')  # Remove the '-p' suffix
                                file_id = file_id.replace('\n', '')
                                a = list(distances.keys())
                                if file_id in a:
                                    dist_data = distances[file_id]
                                    total_disturbed += dist_data['disturbed']
                                    count_disturbed += 1
                                    total_disturbed_p += dist_data['disturbed_p']
                                    count_disturbed_p += 1
                                else:
                                    print(a)


    avg_disturbed = total_disturbed / count_disturbed if count_disturbed > 0 else 0
    avg_disturbed_p = total_disturbed_p / count_disturbed_p if count_disturbed_p > 0 else 0

    return avg_disturbed, avg_disturbed_p
# 加载distances.jsonl文件

distances = load_distances(distances_file)
# 计算fixresultp文件夹中的平均值

avg_disturbed, avg_disturbed_p = calculate_averages_for_valid_files(fixresultp_dir, distances)

print(f"Average disturbed distance: {avg_disturbed}")
print(f"Average disturbed_p distance: {avg_disturbed_p}")

