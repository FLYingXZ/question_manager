#存储所有页面路由
from config import app, handler, VIDEO_FOLDER, load_config
from models import Question, db, Link, User, LoginRecord, DownloadRecord, Exam, Chapter, Section, Material, Post, Reply, RouteLog, LearningMaterial,LearningMaterialClass,Class
from flask import render_template, url_for, request, jsonify, send_from_directory, g
from control import VIDEO_FOLDER, log_request_info
from utils import convert_relative_paths_to_absolute
import os
from datetime import datetime, date
from flask_login import login_required
from users import current_user, permissions_required
import json
from sqlalchemy import desc, func, case

#编程可视化
@app.route("/code_vis")
def code_vis():
    log_request_info('code_vis', current_user, '访问代码动画')
    return render_template("code_vis.html")

@app.route('/gpt')
@login_required
def gpt():
    user = current_user  # 获取当前用户
    
    # 获取当前日期，如果今天的日期与用户上次请求的日期不同，则重置请求次数
    today = date.today()
    if user.last_request_date != today:
        user.request_count = 0
        user.last_request_date = today
        db.session.commit()  # 提交更改
    
    # 获取剩余次数
    remaining = 10 - user.request_count
    
    #chat_history = user.chat_history
    log_request_info('gpt', current_user, '访问GPT')
    return render_template('gpt.html', remaining=remaining)



@app.route('/sim')
@login_required
@permissions_required('is_admin')
def sim():
    log_request_info('sim', current_user, '访问查重页面')
    return render_template('admin/sim.html')

@app.route('/learning_markdown')
#@login_required
def learning_markdown():
    log_request_info('learning_markdown', current_user, '访问学习中心')
    return render_template('learning_markdown.html', user=current_user)


# 学生端课件列表页面
@app.route('/learning_materials_student')
@login_required
def list_learning_materials_student():
    if current_user.is_admin():
        materials = LearningMaterial.query.all()
    else:
        # 仅显示当前用户所在班级的课件
        materials = LearningMaterial.query.join(LearningMaterial.classes).filter(Class.id == current_user.class_id).all()
    log_request_info('learning_materials_student', current_user, '访问学生端课件列表')
    return render_template('learning_materials_list.html', materials=materials)

# 学生端课件详情页面
@app.route('/view_learning_material/<int:material_id>')
@login_required
def view_learning_material(material_id):
    material = LearningMaterial.query.get_or_404(material_id)
    if current_user.class_id not in [cls.id for cls in material.classes] and current_user.role != 'admin':
        return jsonify({'error': '无权访问该课件'}), 403
    log_request_info('view_learning_material', current_user, f'访问学生端课件{material_id}')
    return render_template('view_learning_material.html', material=material)

# 管理员课件列表页面
@app.route('/learning_materials')
def list_learning_materials():
    materials = LearningMaterial.query.all()
    log_request_info('learning_materials', current_user, '访问管理员课件')
    return render_template('admin/learning_materials_list.html', materials=materials)
    
#学生导航栏
@app.route('/navigation')
@login_required
def navigation():
    log_request_info('navigation', current_user, '访问导航栏')
    return render_template('navigation.html')

#配置设置页面
@app.route('/config')
@login_required
@permissions_required('is_admin')
def config():
    config_data = load_config()
    log_request_info('config', current_user, '访问配置页面')
    return render_template('admin/config.html', config_data=config_data)

#查看所有操作记录
@app.route('/logs', methods=['GET'])
@login_required
@permissions_required('is_admin')
def logs():
    page = request.args.get('page', 1, type=int)  # 获取页码，默认为第 1 页
    per_page = 100  # 每页显示的记录数量
    logs = RouteLog.query.order_by(RouteLog.access_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    #log_request_info('logs', current_user, '查看操作记录')
    return render_template('admin/logs.html', logs=logs)

#上下文，使得user_role能够在模板header.html中使用
@app.context_processor
def inject_user_role():
    user_role = getattr(current_user, 'role', None)
    return dict(user_role=user_role)

#测试页面
@app.route('/export_docx')
def export_docx():
    return render_template('export_docx.html')

# 编辑器页面
@app.route('/editor')
@login_required
def editor():
    log_request_info('export_docx', current_user, '访问编辑器')
    return render_template('editor.html')    

#历史上的今天
# 读取json文件的函数，根据当前日期获取事件
def get_history_events():
    # 获取当前的日期
    today = datetime.today()
    month = today.month
    day = today.day

    filename = os.path.join(app.static_folder, 'history_today', f'{month}month_history_toDay.json')
    if not os.path.exists(filename):
        return []

    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # 返回当天的所有事件
    return data[day-1] if len(data) >= day else []

@app.route('/history_today')
def history_today_page():
    events = get_history_events()
    log_request_info('history_today', current_user, '访问历史上的今天')
    return render_template('history_today.html', events=events)

#登录页面
@app.route('/sign_in')
@login_required
def sign_in_page():
    return render_template('sign_in.html')

#登录管理页面
@app.route('/sign_manage')
@login_required
@permissions_required('is_admin')
def sign_manage_page():
    log_request_info('sign_manage', current_user, '查看签到管理页面')
    return render_template('admin/sign_manage.html')

# 视频播放中的一起看设置
@app.route('/yiqikan')
def yiqikan_page():
    return render_template('v2_website.html')

#论坛功能
@app.route('/forum')
@login_required
def forum_page():
    # Subquery to get the latest reply time for each post
    latest_reply_time_subquery = db.session.query(
        Reply.post_id,
        func.max(Reply.create_time).label('latest_reply_time')
    ).group_by(Reply.post_id).subquery()
    
    # Main query to get posts, sorted by the latest reply time (or post create time if no replies)
    posts = db.session.query(Post).outerjoin(
        latest_reply_time_subquery,
        Post.id == latest_reply_time_subquery.c.post_id
    ).order_by(
        desc(case(
            (latest_reply_time_subquery.c.latest_reply_time.isnot(None), latest_reply_time_subquery.c.latest_reply_time),
            else_=Post.create_time
        ))
    ).all()
    
    context = { 
        'posts': posts
    }
    log_request_info('forum', current_user, '访问论坛')
    return render_template('forum.html', **context, user=current_user, len=len)

#查看用户登录情况
@app.route('/login_records')
@login_required
@permissions_required('is_admin')
def login_records_page():
    log_request_info('login_records', current_user)
    return render_template('login_records.html')
    
#个人考试结果查询
@app.route('/user_exam_results/<int:exam_id>', methods=['GET'])
@login_required
def user_exam_results_page(exam_id):
    query_user_id = request.args.get('user_id', type=int)
    # 如果不带 user_id，就默认查看自己
    if not query_user_id:
        query_user_id = current_user.id

    # 如果当前登录的不是 admin/teacher，而 query_user_id != current_user.id => 拒绝
    if current_user.role not in ['admin', 'teacher'] and query_user_id != current_user.id:
        return render_template('403.html'), 403

    # 记录日志
    log_request_info(
        'user_exam_results' + str(exam_id),
        current_user,
        f'访问考试结果 exam_id={exam_id}, user_id={query_user_id}'
    )
    
    return render_template('user_exam_results.html', exam_id=exam_id, user_id=query_user_id)

#问题列表
@app.route('/problem_list')
@login_required
def problem_list():
    is_admin_or_teacher = current_user.role=='admin' or current_user.role=='teacher'
    log_request_info('problem_list', current_user, '访问问题列表')
    return render_template(
        'admin/problem_list.html',
        is_admin_or_teacher=is_admin_or_teacher
    )

#用户管理
@app.route('/users_manage')
@login_required
@permissions_required('is_admin', 'is_teacher')
def users_manage_page():
    log_request_info('users_manage', current_user, '访问用户管理')
    return render_template('admin/users_manage.html')

#班级管理
@app.route('/manage_classes')
@login_required
@permissions_required('is_admin', 'is_teacher')
def manage_classes_page():
    log_request_info('manage_classes', current_user, '访问班级管理')
    return render_template('admin/manage_classes.html')

#考试功能
@app.route('/exam')
@login_required
def exam_page():
    log_request_info('exam', current_user, '访问考试功能')
    return render_template('exam.html')

#考试页面
@app.route('/exam_list')
@login_required
def exam_list_page():
    log_request_info('exam_list', current_user, '访问考试管理')
    return render_template('exam_list.html')

@app.route('/exam_statistics_page/<int:exam_id>', methods=['GET'])
@login_required
@permissions_required('is_admin', 'is_teacher', 'is_student')
def exam_statistics_page(exam_id):
    log_request_info('exam_statistics_page/'+str(exam_id), current_user, '访问考试统计'+str(exam_id))
    exam = Exam.query.get_or_404(exam_id)
    return render_template('exam_statistics.html', exam=exam)

#项目文档
@app.route('/help')
@login_required
def help_page():
    log_request_info('help', current_user, '访问项目文档')
    return render_template('admin/help.html')
#登录页面
@app.route('/login')
def login_page():
    return render_template('login_page.html')
#注册页面
@app.route('/register')
def register_page():
    return "暂未开通 !"
    #return render_template('register_page.html')
#添加题目
@app.route('/add_question')
@login_required
@permissions_required('is_admin', 'is_teacher')
def add_question_page():
    log_request_info('add_question', current_user, '添加题目')
    return render_template('admin/add_question.html')

#个人资料
@app.route('/profile')
@login_required
def profile_page():
    log_request_info('profile', current_user, '访问个人资料')
    user = current_user
    download_records = user.downloads.order_by(DownloadRecord.last_download_time.desc()).all()  # 按下载时间倒序获取当前用户的下载记录
    return render_template('profile.html', user=user.to_dict(), download_records=[record.to_dict() for record in download_records])

#学习文件页面
@app.route('/document')
@login_required
def document_page():
    chapters = Chapter.query.all()
    return render_template('document.html', chapters=chapters, current_user_role=current_user.role)

#生成预览URL
@app.route('/get_preview_url/<filename>')
def get_preview_url(filename):
    # Assuming that 'UPLOAD_FOLDER' is configured properly in the app config
    file_url = url_for('download_document', filename=filename)
    filetype = filename.split('.')[-1]
    return jsonify({'file_url': file_url, 'filetype': filetype})
#预览
@app.route('/preview_document/<filename>')
def preview_document(filename):
    file_url = url_for('static', filename=f'documents/{filename}')
    return render_template('preview.html', file_url=file_url)

#文件上传
@app.route('/upload')
#@login_required
#@permissions_required('is_admin', 'is_teacher')
def upload_page():
    log_request_info('upload', current_user, '访问文件上传')
    return render_template('admin/upload.html')
#视频列表
@app.route('/videos')
@login_required  # 确保只有登录的用户才能访问
@permissions_required('is_admin')
def list_videos_page():
    log_request_info('videos', current_user, '访问视频列表')
    videos = os.listdir(VIDEO_FOLDER)
    videos = sorted(videos)
    return render_template('admin/list_videos.html', videos=videos)

#告白页
from flask import session
app.secret_key = 'your_secret_key'  # 必须设置secret_key才能使用session
# 设置密码和错误次数上限
PASSWORD = '19960122'
MAX_ATTEMPTS = 10
@app.route('/love', methods=['GET', 'POST'])
def love():
    #log_request_info('***', 'Unknow', '***')
    if 'attempts' not in session:
        session['attempts'] = 0
    
    if session['attempts'] >= MAX_ATTEMPTS:
        return "输入错误次数超过限制，无法再输入密码。"

    if request.method == 'POST':
        entered_password = request.form.get('password')

        if entered_password == PASSWORD:
            session.pop('attempts', None)  # 重置尝试次数
            return render_template('admin/love.html')
        else:
            session['attempts'] += 1
            return "密码错误，请重试。"

    return '''
        <form method="POST">
            <label>请输入密码（提示：波的生日，8位数字）：</label>
            <input type="password" name="password">
            <input type="submit" value="提交">
        </form>
    '''
#工具箱
@app.route('/friend')
@login_required
@permissions_required('is_admin')
def friend_page():
    log_request_info('friend', current_user, '访问工具箱')
    links = Link.query.all()
    grouped_links = {}

    for link in links:
        if link.grp not in grouped_links:
            grouped_links[link.grp] = [link]
        else:
            grouped_links[link.grp].append(link)

    return render_template('admin/friend.html', grouped_links=grouped_links)