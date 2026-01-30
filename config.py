# 从 Flask 框架中导入 Flask 类，用于创建应用实例
# request用于处理请求数据，jsonify用于返回 JSON 格式响应
# render_template用于渲染 HTML 模板
from flask import Flask
from flask_cors import CORS
# 用于管理文件上传，特别是图像
from flask_uploads import UploadSet, configure_uploads, IMAGES

# 导入 logging 模块用于记录日志
from logging.handlers import RotatingFileHandler  # 导入日志处理器，可以设置日志轮换
import logging, os, json

# 初始化 Flask 应用实例
app = Flask(__name__)
# 启用 CORS，允许所有来源
CORS(app)
# 设置日志文件的路径和日志文件的滚动策略
handler = RotatingFileHandler('./uploads/files/visit.log', maxBytes=10000, backupCount=3)
logging.basicConfig(filename='app.log', level=logging.INFO)
# 获取日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 设置日志级别为 INFO
logger.addHandler(handler)  # 添加处理器到日志记录器

# 配置 Flask 应用的密钥和数据库 URI
app.config['SECRET_KEY'] = 'miku'  # 应用密钥，用于会话管理等
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'questions.db')  # SQLite 数据库路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭数据库修改跟踪（可以提高性能）

# 创建 UploadSet 实例，用于处理图像文件的上传
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'  # 设置上传图像的目标目录
app.config['UPLOAD_FOLDER'] = 'uploads/files'  # 设置文件上传的目标目录
app.config['UPLOAD_HTML_FOLDER'] = 'uploads/html'  # 设置文件上传的目标目录

# 配置应用的文件上传功能
configure_uploads(app, photos)

# 定义视频上传目录
VIDEO_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
if not os.path.exists(VIDEO_FOLDER):  # 如果目录不存在，则创建
    os.makedirs(VIDEO_FOLDER)
# 加载配置文件
def load_config():
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    app.config['ALLOWED_IPS'] = config_data['ALLOWED_IPS']
    app.config['BAIDU_GPT_ID'] = config_data['BAIDU_GPT_ID']
    app.config['BAIDU_GPT_SECRET_KEY'] = config_data['BAIDU_GPT_SECRET_KEY']
    app.config['CHATGPT_KEY'] = config_data['CHATGPT_KEY']
    app.config['CHATGPT_BASE_URL'] = config_data['CHATGPT_BASE_URL']
    app.config['SPARKAI_URL'] = config_data['SPARKAI_URL']
    app.config['SPARKAI_APP_ID'] = config_data['SPARKAI_APP_ID']
    app.config['SPARKAI_API_SECRET'] = config_data['SPARKAI_API_SECRET']
    app.config['SPARKAI_API_KEY'] = config_data['SPARKAI_API_KEY']
    return config_data

load_config()
