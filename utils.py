#题目判重
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import numpy as np
from config import app, logger
from datetime import datetime
from flask import Flask, request, jsonify, render_template, url_for
import os, json, requests
from flask_uploads import UploadSet, configure_uploads, IMAGES

#相似度检测
def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
    return similarity.item()

#转换相对路径为绝对路径
import re
def convert_relative_paths_to_absolute(content):
    base_url = 'https://www.flying.zj.cn'  # 将此更改为你的实际主机地址
    def replace_match(match):
        relative_path = match.group(1)
        absolute_path = f"{base_url}/{relative_path}"
        return f'src="{absolute_path}"'
    
    pattern = re.compile(r'src="(_uploads/photos/[^"]+)"')
    converted_content = pattern.sub(replace_match, content)
    return converted_content

def secure_filename_with_chinese(filename):
    # 只允许中文字符、字母、数字、点、下划线和短横线
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # 防止文件名太长
    return filename[:100]

#IP白名单，开发中
from flask import request, abort
def ip_required(allowed_ips):
    def decorator(f):
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr
            flag = False
            for IP in allowed_ips:
                if IP in str(client_ip):
                    flag = True
            if not flag:
                abort(403)  # 禁止访问
            return f(*args, **kwargs)
        return wrapped
    return decorator

#ChatGPT------------------------------------------------------------------------------------------------
from openai import OpenAI
client = OpenAI(
    # 使用环境变量或直接设置 API 密钥
    api_key=app.config['CHATGPT_KEY'],
    base_url=app.config['CHATGPT_BASE_URL']
)

# 流式传输响应
def gpt_35_api(messages: list, model):
    """为提供的对话消息创建新的回答 (流式传输)

    Args:
        messages (list): 完整的对话消息
    """
    res = ""
    result = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False,
    )
    result = result.choices[0].message.content
    return result

def chatgpt(question, model):
    """支持连续对话，并使用流式传输"""
    messages = [{'role': 'user', 'content': ''}]
    while True:
        # 获取用户输入并添加到对话历史
        user_input = question
        if user_input.lower() in ['exit', 'quit', 'bye']:  # 可以输入退出词退出对话
            print("结束对话.")
            break
        messages.append({'role': 'user', 'content': user_input})

        # 使用流式传输获取模型回复并实时输出
        
        return gpt_35_api(messages, model)

#文心一言4.0--------------------------------------------------------------------------------
BAIDU_GPT_ID = app.config['BAIDU_GPT_ID']
BAIDU_GPT_SECRET_KEY = app.config['BAIDU_GPT_SECRET_KEY']
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id="+BAIDU_GPT_ID+"&client_secret="+BAIDU_GPT_SECRET_KEY
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def call_baidu_gpt_api(content):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + get_access_token()
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response["result"]
#科大讯飞星火大模型GPT----------------------------------------------------------------------
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
# 配置讯飞API用户信息
#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = app.config['SPARKAI_URL']
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = app.config['SPARKAI_APP_ID']
SPARKAI_API_SECRET = app.config['SPARKAI_API_SECRET']
SPARKAI_API_KEY = app.config['SPARKAI_API_KEY']
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'
spark = ChatSparkLLM(
    spark_api_url=SPARKAI_URL,
    spark_app_id=SPARKAI_APP_ID,
    spark_api_key=SPARKAI_API_KEY,
    spark_api_secret=SPARKAI_API_SECRET,
    spark_llm_domain=SPARKAI_DOMAIN,
    streaming=False
)
#以下为星火GPT的调用

handler = ChunkPrintHandler()
def call_xunfei_gpt(question):
    messages = [ChatMessage(
        role="user",
        content=question
    )]
    return spark.generate([messages], callbacks=[handler])
#IP获取
#def log_request_info(page, user):
#    if str(user)=='<User 1>': return
#    # 尝试从 X-Forwarded-For 头信息中获取 IP 地址
#    ip = request.headers.get('X-Real-IP', request.remote_addr).split(',')[0].strip()
#    if check_allowed_ip(ip, ALLOWED_IPS):
#        return
#    location = get_ip_location(ip)
#    time = datetime.now()
#    user = user
#    logger.info(f"{user} from {ip} ({location}) at {time}  visit: {page}")
#IP地理位置