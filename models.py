# 存储数据模型，直接与数据库关联，并且可以通过模型操作数据库
# 包含模型：问题、工具链接、B站视频号

from config import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from utils import convert_relative_paths_to_absolute
from sqlalchemy.dialects.sqlite import JSON

# 关键语句，创建数据库实例，如此可以利用接口直接操作数据库而避免编写sql语句
db = SQLAlchemy(app)
from flask import Flask, request, jsonify, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES
import json
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.ext.declarative import declarative_base

# AI对话会话表
class AISession(db.Model):
    __tablename__ = 'ai_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 根据您的用户表名调整
    title = db.Column(db.String(200), nullable=False, default='新对话')
    model_used = db.Column(db.String(100), nullable=False)
    prompt_template = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    messages = db.relationship('AIMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='ai_sessions')  # 根据您的用户模型调整

# 对话消息表
class AIMessage(db.Model):
    __tablename__ = 'ai_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('ai_sessions.id'), nullable=False)
    role = db.Column(db.Enum('system', 'user', 'assistant', name='message_roles'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tokens = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 预设prompt模板表
class AIPromptTemplate(db.Model):
    __tablename__ = 'ai_prompt_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    variables = db.Column(JSON)  # 存储变量名列表，如 ["code", "input", "sol", "problem"]
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# AI模型配置表
class AIModelConfig(db.Model):
    __tablename__ = 'ai_model_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    api_url = db.Column(db.String(500), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    max_tokens = db.Column(db.Integer, default=4000)
    temperature = db.Column(db.Float, default=0.7)
    is_active = db.Column(db.Boolean, default=True)
    
    # 新增权限控制字段
    allowed_roles = db.Column(db.JSON, default=['admin', 'teacher', 'student', 'user'])  # 允许使用的角色
    priority = db.Column(db.Integer, default=0)  # 优先级，用于排序
    require_login = db.Column(db.Boolean, default=True)  # 是否需要登录
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'api_url': self.api_url,
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'is_active': self.is_active,
            'allowed_roles': self.allowed_roles or ['admin', 'teacher', 'student', 'user'],
            'priority': self.priority,
            'require_login': self.require_login,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def can_access(self, user_role, is_authenticated):
        """检查用户是否有权限使用该模型"""
        if not self.is_active:
            return False
        
        if self.require_login and not is_authenticated:
            return False
            
        # 处理 allowed_roles 为 None 的情况
        allowed_roles = self.allowed_roles or ['admin', 'teacher', 'student', 'user']
        
        if user_role in allowed_roles:
            return True
            
        return False
    
class AIApiKey(db.Model):
    __tablename__ = 'ai_api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#html管理类
class HTMLPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100))

#推荐阅读
class RecommendedReading(db.Model):
    __tablename__ = 'recommended_readings'
    id = db.Column(db.Integer, primary_key=True)                #id
    title = db.Column(db.String(255), nullable=False)           #标题
    url = db.Column(db.String(255), nullable=False)             #链接
    date_added = db.Column(db.DateTime, default=datetime.now)   #创建时间
    image_url = db.Column(db.String(255), nullable=True)       #标题图片链接
    def __repr__(self):
        return f'<RecommendedReading {self.title}>'

# 公告模型
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)                    #id
    title = db.Column(db.String(200), nullable=False)               #标题
    content = db.Column(db.Text, nullable=False)                    #内容
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  #创建时间
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_id_Notice'))  #外键：作者id
    author = db.relationship('User', backref='notices')                                     #作者

# 课堂学习模型
class LearningMaterial(db.Model):
    __tablename__ = 'learning_materials'
    id = db.Column(db.Integer, primary_key=True)                                #id
    title = db.Column(db.String(255), nullable=False)                           #标题
    content = db.Column(db.Text, nullable=False)                                #内容
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())    #创建时间
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_id_learningmaterial'))#外键：作者id
    classes = db.relationship(
        'Class',
        secondary='learning_material_class',
        back_populates='learning_materials'
    )
    creator = db.relationship('User', backref='created_materials', lazy='joined')

    def __repr__(self):
        return f"<LearningMaterial {self.title}>"


# 关联表：学习资料与班级的多对多关系
class LearningMaterialClass(db.Model):
    __tablename__ = 'learning_material_class'
    material_id = db.Column(db.Integer, db.ForeignKey('learning_materials.id'), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), primary_key=True)


#操作记录模型
class RouteLog(db.Model):
    __tablename__ = 'route_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_id_routelog', ondelete='CASCADE'), nullable=True)
    user_name = db.Column(db.String(64))
    ip_address = db.Column(db.String(64))
    access_time = db.Column(db.DateTime, default=datetime.now)
    page = db.Column(db.String(128))
    location = db.Column(db.String(128), nullable=True)  # IP 地理位置信息
    extra_info = db.Column(db.String(256), nullable=True)  # 其他信息字段

    user = db.relationship('User', backref=db.backref('route_logs', cascade='all, delete-orphan'))



# 签到记录模型类
class SignInRecord(db.Model):
    __tablename__ = 'sign_in_records'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', name='fk_user_id_signin', ondelete='CASCADE'),  # 添加 ondelete='CASCADE'
        nullable=False
    )
    sign_in_date = db.Column(db.Date, nullable=False)  # 签到日期
    sign_in_time = db.Column(db.DateTime, nullable=True)  # 签到时间
    status = db.Column(db.String(10), default='未签到')  # 签到状态：已签到或未签到

    user = db.relationship('User', backref='sign_in_records')  # 关联到用户
    # 添加复合索引
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'sign_in_date'),
    )
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'usernick': self.user.usernick,
            'sign_in_date': self.sign_in_date.strftime('%Y-%m-%d'),
            'sign_in_time': self.sign_in_time.strftime('%Y-%m-%d %H:%M:%S') if self.sign_in_time else None,
            'status': self.status
        }

# 博客模型类
class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_users_id_blog'))
    author = db.relationship('User', backref=db.backref('blogs', lazy='dynamic'))
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'category': self.category,
            'tags': self.tags.split(','),
            'author': self.author.username,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'is_public': self.is_public
        }

# 帖子模型类
class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    title = db.Column(db.String(100), nullable=False)  # 帖子标题
    content = db.Column(db.Text, nullable=False)  # 帖子内容
    create_time = db.Column(db.DateTime, default=datetime.now)  # 帖子创建时间，默认为当前时间
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键，关联到用户表
    author = db.relationship('User', backref=db.backref('posts'))  # 关联用户模型，形成双向关系

# 回复模型类
class Reply(db.Model):
    __tablename__ = 'replys'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    content = db.Column(db.Text, nullable=False)  # 回复内容
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))  # 外键，关联到帖子表
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键，关联到用户表
    create_time = db.Column(db.DateTime, default=datetime.now)  # 回复创建时间，默认为当前时间

    post = db.relationship('Post', backref=db.backref('replys', order_by=create_time.desc()))  # 关联帖子模型，形成双向关系
    author = db.relationship('User', backref=db.backref('replys'))  # 关联用户模型，形成双向关系

# 章模型类
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(100), nullable=False)  # 章的名称
    sections = db.relationship('Section', backref='chapter', lazy=True)  # 关联节模型，形成双向关系

# 节模型类
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(100), nullable=False)  # 节的名称
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)  # 外键，关联到章表
    materials = db.relationship('Material', backref='section', lazy=True)  # 关联学习材料模型，形成双向关系

# 学习材料模型类
class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(100), nullable=False)  # 学习材料名称
    filename = db.Column(db.String(100), nullable=False)  # 文件名
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)  # 外键，关联到节表
    note = db.Column(db.String(200), nullable=True)  # 备注字段，可为空

# 用户班级模型类
class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(120), unique=True, nullable=False)  # 班级名称，唯一且不能为空
    # 通过学习资料关联表与学习资料模型的关系
    learning_materials = db.relationship(
        'LearningMaterial',
        secondary='learning_material_class',
        back_populates='classes'
    )

# 班级与试卷关联表模型类
class ExamClassAssociation(db.Model):
    __tablename__ = 'exam_class_association'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', name='fk_exam_id_exam'), nullable=False)  # 外键，关联到试卷表
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', name='fk_classes_id_class'), nullable=False)  # 外键，关联到班级表

# 试卷模型类
class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(128), nullable=False)  # 试卷名称
    question_ids = db.Column(db.Text, nullable=False)  # 以逗号分隔的题目ID列表
    duration = db.Column(db.Integer, nullable=False)  # 考试时长，单位为分钟
    num_questions = db.Column(db.Integer, nullable=False)  # 选取题目数量
    score_per_question = db.Column(db.Integer, nullable=False, default=0)  # 每道题的分数，默认值为0
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间，默认为当前时间
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_users_id_exam'), nullable=False, default=1)  # 创建者ID，外键关联到用户表
    classes = db.relationship('Class', secondary='exam_class_association', backref=db.backref('exams', lazy='dynamic'))  # 关联班级模型，形成多对多关系
    creator = db.relationship('User', backref='created_exams', lazy='joined') # 添加 creator 关系，用于关联创建者信息

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'question_ids': self.question_ids,
            'duration': self.duration,
            'num_questions': self.num_questions,
            'creator_id': self.creator_id,
            'creator_name': self.creator.username or self.creator.username,  # 获取创建者昵称或用户名
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'score_per_question': self.score_per_question,
            'classes': [cls.id for cls in self.classes]  # 返回班级ID
        }

# 考试会话模型
class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) #开考时间

# 试卷结果模型类
class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_id_users', ondelete='CASCADE'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', name='fk_exam_id_exams', ondelete='CASCADE'), nullable=False)  # 外键，关联到试卷表
    score = db.Column(db.Integer, nullable=False)  # 考试得分
    answers = db.Column(db.Text, nullable=False)  # 用户的答案，以JSON格式存储
    submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 提交时间，默认为当前时间

    __table_args__ = (
        db.Index('idx_user_exam', 'user_id', 'exam_id'),
        db.Index('idx_exam_score', 'exam_id', 'score')
    )

    def get_detailed_answers(self):
        answers = json.loads(self.answers)
        detailed_answers = []
        for question_id, answer in answers.items():
            question = Question.query.get(question_id)
            detailed_answers.append({
                'question_id': question_id,
                'content': convert_relative_paths_to_absolute(question.content),
                'correct_answer': question.answer,
                'user_answer': answer,
                'analysis': convert_relative_paths_to_absolute(question.analysis)
            })
        return detailed_answers

# 用户模型类
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    usernick = db.Column(db.String(64), nullable=True)  # 昵称
    
    telephone = db.Column(db.String(11), nullable=True)  # 电话号码，可为空
    email = db.Column(db.String(120), unique=True, index=True)  # 邮箱，唯一且索引
    password_hash = db.Column(db.String(128))  # 密码哈希值
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', name='fk_class_id_user'))  # 外键，关联到班级表
    role = db.Column(db.String(120))  # 用户角色
    request_count = db.Column(db.Integer, default=0)  # 当天GPT请求次数
    last_request_date = db.Column(db.Date, default=date.today)  # 上次请求日期
    user_class = db.relationship('Class', backref='users', lazy='joined')  # 关联班级模型，形成双向关系
    questions = db.relationship('Question', secondary='user_question_association', back_populates='users') #关联问题表形成双向关系
    exam_results = db.relationship('ExamResult', backref='user', lazy='dynamic')
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    # 增加聊天历史字段，用于存储每个用户的对话历史
    chat_history = db.Column(db.JSON, default=[])  # 使用 JSON 类型存储历史

    def get_chat_history(self):
        return self.chat_history

    def add_to_chat_history(self, message):
        # 确保每个用户的聊天历史独立
        if not self.chat_history:
            self.chat_history = []
        
        # 添加时间戳
        from datetime import datetime
        message['timestamp'] = datetime.utcnow().isoformat()
        
        self.chat_history.append(message)
        db.session.commit()  # 提交到数据库
        
    def get_class_name(self):
        if self.user_class:
            return self.user_class.name
        return None

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')  # 密码不可读
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # 设置密码时生成哈希值
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)  # 验证密码
    def is_admin(self):
        return self.role == 'admin'  # 判断是否为管理员
    def is_teacher(self):
        return self.role == 'teacher'  # 判断是否为教师
    def is_student(self):
        return self.role == 'student'  # 判断是否为学生
    def is_user(self):
        return self.role == 'user'  # 判断是否为普通用户

    downloads = db.relationship('DownloadRecord', backref='user', lazy='dynamic')  # 关联下载记录模型，形成双向关系

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'usernick': self.usernick,
            'email': self.email,
            'class_id': self.class_id,
            'role': self.role,
            'class_name': self.get_class_name(),  # 返回班级名称
            'is_admin': self.is_admin(),
            'is_teacher': self.is_teacher(),
            'is_student': self.is_student(),
            'is_user': self.is_user(),
            'downloads': [download.to_dict() for download in self.downloads],
            'avatar_url': 'https://q1.qlogo.cn/g?b=qq&nk=' + self.email +'&s=100' if 'qq.com' in self.email else '/static/images/1110055.png',  # 头像URL
            'request_count': self.request_count,  # 返回当前请求次数
        }

# 登录行为记录模型类
class LoginRecord(db.Model):
    __tablename__ = 'loginRecord'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(64), index=True)  # 用户名，索引
    ip_address = db.Column(db.String(64))  # IP地址
    login_time = db.Column(db.DateTime, default=datetime.now)  # 登录时间，默认为当前时间

    def __repr__(self):
        return '<LoginRecord {}>'.format(self.username)

# 下载题目记录模型类
class DownloadRecord(db.Model):
    __tablename__ = 'download_records'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # 外键，关联到用户表
    list_name = db.Column(db.String(128))  # 题目清单名称
    list_value = db.Column(db.String(128))  # 题目清单
    last_download_time = db.Column(db.DateTime, default=datetime.now)  # 最后下载时间，默认为当前时间

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'list_name': self.list_name,
            'list_value': self.list_value,
            'last_download_time': self.last_download_time
        }

    def __repr__(self):
        return '<DownloadRecord user_id={}, list_name={}>'.format(self.user_id, self.list_name)

#问题与用户关联表
class UserQuestionAssociation(db.Model):
    __tablename__ = 'user_question_association'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint('user_id', 'question_id', name='uq_user_question'),)

# 问题模型类
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    content = db.Column(db.Text, nullable=False)  # 问题内容（HTML）
    content_text = db.Column(db.Text)  # 解析HTML后的纯文本内容
    knowledge_point = db.Column(db.Text)  # 知识点
    difficulty = db.Column(db.Integer)  # 难度
    source = db.Column(db.Text)  # 来源
    answer = db.Column(db.Text, nullable=False)  # 答案
    analysis = db.Column(db.Text)  # 解析
    description = db.Column(db.Text, nullable=True)  # 问题描述，可为空
    qtype = db.Column(db.Integer, default=0)  # 题型，0为未设置，1为选择题，2为材料题，3为综合题
    attempts = db.Column(db.Integer, default=0)  # 做题次数，默认值为0
    correct_answers = db.Column(db.Integer, default=0)  # 正确次数，默认值为0
    exam_attempts = db.Column(db.Integer, default=0)  # 在试卷中的做题次数，默认值为0
    exam_correct_answers = db.Column(db.Integer, default=0)  # 在试卷中的正确次数，默认值为0
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间，默认为当前时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())# 更新时间，默认为当前时间且在更新时自动更新
    users = db.relationship('User', secondary='user_question_association', back_populates='questions') #关联添加题目的管理员用户表形成双向关系
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'content_text': self.content_text,
            'knowledge_point': self.knowledge_point,
            'difficulty': self.difficulty,
            'source': self.source,
            'answer': self.answer,
            'analysis': self.analysis,
            'attempts': self.attempts,
            'qtype': self.qtype,
            'description': self.description,
            'correct_answers': self.correct_answers,
            'exam_attempts': self.exam_attempts,
            'exam_correct_answers': self.exam_correct_answers,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

class chongbuluo_URL(db.Model):
    __tablename__ = 'chongbuluo_url'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    url = db.Column(db.String(255), nullable=False)  # 链接URL
    title = db.Column(db.String(255), nullable=False)  # 链接标题
    description = db.Column(db.String(255))  # 链接描述，可为空
    author = db.Column(db.String(255))  # 作者描述，可为空
    grp = db.Column(db.String(255))  #分类

# 工具链接模型类
class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    url = db.Column(db.String(255), nullable=False)  # 链接URL
    title = db.Column(db.String(255), nullable=False)  # 链接标题
    description = db.Column(db.String(255))  # 链接描述，可为空
    grp = db.Column(db.String(255))  # 组别

    def __repr__(self):
        return f'<Link {self.title}>'

# 知识点模型类
class KnowledgePoint(db.Model):
    __tablename__ = 'knowledgepoint'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    module = db.Column(db.String(120), nullable=False)  # 知识点所属模块
    knowledgepoint = db.Column(db.String(120), nullable=False)  # 知识点名称

    def to_dict(self):
        return {
            'id': self.id,
            'module': self.module,
            'knowledgepoint': self.knowledgepoint
        }
