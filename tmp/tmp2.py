import re

# 读取output.txt文件内容
with open('output.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# 匹配形如“static/images/2024052607313012912.png”的文件名
pattern = r"static/images/([\w]+\.jpeg)"
matches = re.findall(pattern, content)

# 将结果写入新的文件
with open('jpg_files_list.txt', 'w', encoding='utf-8') as output_file:
    for match in matches:
        output_file.write(match + '\n')

print(f"提取完成，共找到 {len(matches)} 个PNG文件名。文件已保存为 jpg_files_list.txt")
