import requests
import os

# 设置下载文件的前缀URL
base_url = "https://xxjstk.top/static/images/"

# 输出目录
output_dir = "downloads"
os.makedirs(output_dir, exist_ok=True)  # 如果目录不存在，创建目录

# 读取文件列表
with open("jpg_files_list.txt", "r") as file:
    file_names = [line.strip() for line in file.readlines() if line.strip()]

# 下载每个文件
for file_name in file_names:
    url = base_url + file_name
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查HTTP请求是否成功
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {file_name}")
    except requests.RequestException as e:
        print(f"Failed to download {file_name}: {e}")
