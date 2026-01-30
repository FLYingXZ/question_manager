import os
import json

# 定义关键词
keywords = ["女优", "日本女演员"]

# 获取当前文件夹中的所有 JSON 文件
json_files = [f for f in os.listdir() if f.endswith('.json')]

# 遍历所有 JSON 文件
for file_name in json_files:
    # 打开 JSON 文件并加载数据
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 如果数据是列表类型，过滤包含关键词的条目
    if isinstance(data, list):
        data = [entry for entry in data if not any(keyword in json.dumps(entry, ensure_ascii=False) for keyword in keywords)]
    
    # 如果数据是字典类型，可以根据特定的字段来过滤
    elif isinstance(data, dict):
        data = {key: value for key, value in data.items() if not any(keyword in json.dumps(value, ensure_ascii=False) for keyword in keywords)}
    
    # 将修改后的数据写回文件
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

print("所有包含关键词的条目已删除并保存。")
