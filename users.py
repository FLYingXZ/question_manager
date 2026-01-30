#存储所有页面路由
from config import app, handler, logger
from models import db, User, LoginRecord, Class, RouteLog, SignInRecord, ExamResult
from flask import render_template, url_for, request, Flask, jsonify, redirect
from utils import ip_required
import os
from datetime import datetime, timedelta

#用户功能
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user, LoginManager, login_user, UserMixin, logout_user

# 设置会话和cookie的有效期
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)  # 设置"记住我"功能的有效期

# 权限装饰器
from functools import wraps
def permissions_required(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if any(getattr(current_user, permission)() for permission in permissions):
                return f(*args, **kwargs)
            return jsonify({'message': '权限不足'}), 403
        return decorated_function
    return decorator


# 注册
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
    
        # 检查邮箱是否已被注册
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': '邮箱已注册'}), 400
        
        # 获取班级ID
        class_id = None
        if data.get('class_name'):
            user_class = Class.query.filter_by(name=data['class_name']).first()
            if user_class:
                class_id = user_class.id
            else:
                class_id = 5

        user = User(
            username=data['username'],
            usernick=data['usernick'],
            email=data['email'],
            password=data['password'],  # 利用User模型中的password setter自动处理
            class_id=class_id,  # 关联到班级
            role='student'  # 默认角色
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': '注册成功！', 'redirect': url_for('problem_list')}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更换密码
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'message': '请填写旧密码和新密码'}), 400
        
        user = current_user
        
        if not user.verify_password(old_password):
            return jsonify({'message': '旧密码错误'}), 400
        
        user.password = new_password
        db.session.commit()
        
        return jsonify({'message': '密码更换成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更换邮箱
@app.route('/change_email', methods=['POST'])
@login_required
def change_email():
    data = request.get_json()
    new_email = data.get('new_email')

    if not new_email:
        return jsonify({'message': '新邮箱不能为空'}), 400

    if User.query.filter_by(email=new_email).first():
        return jsonify({'message': '该邮箱已被使用'}), 400

    current_user.email = new_email
    db.session.commit()

    return jsonify({'message': '邮箱更换成功'})

#登录
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"  #未登录时重定向到登录页

# 设置会话保护
login_manager.session_protection = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '请填写用户名或密码'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        # 检查用户上次登录时间是否超过7天
        # if user.last_login and (datetime.now() - user.last_login).days >= 30 and user.last_login:
        #     logout_user()  # 强制用户登出# 更新用户的登录时间
        #     user.last_login = datetime.now()
        #     db.session.commit()
        #     return jsonify({'message': '您的会话已过期，请重新登录！'}), 401

        # 登录用户
        login_user(user, remember=True)

        # 更新用户的登录时间
        #user.last_login = datetime.now()
        #db.session.commit()

        # 获取用户IP和当前时间
        user_ip = request.headers.get('X-Real-IP', request.remote_addr).split(',')[0].strip()
        current_time = datetime.now()

        # 保存登录记录
        if not (user_ip.startswith('60.191.201.') or user_ip.startswith('60.191.227.')):
            login_record = LoginRecord(username=username, ip_address=user_ip, login_time=current_time)
            db.session.add(login_record)
            db.session.commit()

        # 登录成功，重定向到相应页面
        if user.role == 'student':
            return jsonify({'message': '登录成功！', 'redirect': url_for('sign_in_page')}), 200
        else:
            return jsonify({'message': '登录成功！', 'redirect': url_for('notice_page')}), 200

    return jsonify({'message': '用户名或密码错误！'}), 401

#登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('problem_list'))  # 重定向到登录页面

#获取当前用户角色
@app.route('/current_user_role', methods=['GET'])
@login_required
def current_user_role():
    return jsonify(current_user.role)

#登录记录
@app.route('/get_login_records')
@login_required
@permissions_required('is_admin')
def get_login_records():
    page = request.args.get('page', 1, type=int)  # 获取页码，默认值为1
    per_page = request.args.get('per_page', 500, type=int)  # 每页记录数，默认值为500
    pagination = LoginRecord.query.order_by(LoginRecord.login_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    return jsonify({
        'records': [{'username': record.username, 'ip_address': record.ip_address, 'login_time': record.login_time.strftime('%Y-%m-%d %H:%M:%S')} for record in records],
        'total_pages': pagination.pages,
        'current_page': page
    })

    
    
# 用户管理
@app.route('/users', methods=['GET'])
@login_required
@permissions_required('is_admin', 'is_teacher')
def get_users():
    try:
    
        # 获取分页参数，默认为第 1 页，每页显示 100 个用户
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        search_query = request.args.get('search', '', type=str)
    
        # 查询用户，如果有搜索关键字则添加过滤条件
        query = User.query
        if search_query:
            search = f"%{search_query}%"
            query = User.query.join(User.user_class).filter(
                (User.username.ilike(search)) |  # 搜索用户名
                (User.usernick.ilike(search)) |  # 搜索昵称
                (User.email.ilike(search))    |  # 搜索邮箱
                (User.role.ilike(search))     |  # 搜索角色
                (Class.name.ilike(search))       # 搜索班级
            )
    
        # 进行分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
        # 返回用户数据及分页信息
        users = [user.to_dict() for user in pagination.items]
        return jsonify({
            'users': users,
            'total': pagination.total,  # 总用户数
            'pages': pagination.pages,  # 总页数
            'current_page': pagination.page,  # 当前页码
            'per_page': pagination.per_page  # 每页显示的用户数
        })

    except Exception as e:
        return jsonify({"error": "获取用户列表失败:"+str(e)}), 500


@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
@permissions_required('is_admin', 'is_teacher')
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/user', methods=['POST'])
@login_required
@permissions_required('is_admin', 'is_teacher')
def add_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '邮箱已注册'}), 400

    class_id = None
    if data.get('class_name'):
        user_class = Class.query.filter_by(name=data['class_name']).first()
        if user_class:
            class_id = user_class.id
        else:
            return jsonify({'message': '班级不存在'}), 400

    user = User(
        username=data['username'],
        usernick=data['usernick'],
        email=data['email'],
        password=data['password'],
        class_id=class_id,
        role=data.get('role', 'student'),
        request_count = data['request_count']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': '用户添加成功！'}), 201

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
@permissions_required('is_admin', 'is_teacher')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = data['username']
    if 'usernick' in data:
        if data['usernick'] != "":
            user.usernick = data['usernick']
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': '邮箱已注册'}), 400
        user.email = data['email']
    if 'password' in data:
        if data['password'] != "":
            user.password = data['password']
    if 'class_name' in data:
        user_class = Class.query.filter_by(name=data['class_name']).first()
        if user_class:
            user.class_id = user_class.id
        else:
            return jsonify({'message': '班级不存在'}), 400
    if 'role' in data:
        user.role = data['role']
    user.request_count = data['request_count']
    db.session.commit()
    return jsonify({'message': '用户更新成功！'})

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
@permissions_required('is_admin')
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # 先删除签到记录
        SignInRecord.query.filter_by(user_id=user_id).delete()
        # 删除考试记录
        ExamResult.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '用户删除成功！'})
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e) }), 500
        
@app.route('/users/batch_delete', methods=['POST'])
@login_required
@permissions_required('is_admin')
def batch_delete_users():
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])

        if not user_ids:
            return jsonify({'message': '未选择任何用户'}), 400

        # 防止误删自己（可选）
        if current_user.id in user_ids:
            return jsonify({'message': '不能删除当前登录用户'}), 400

        # 先删除关联表记录
        # 签到记录
        SignInRecord.query.filter(SignInRecord.user_id.in_(user_ids)).delete(synchronize_session=False)
        # 考试记录
        ExamResult.query.filter(ExamResult.user_id.in_(user_ids)).delete(synchronize_session=False)

        # 再删除用户
        User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)

        db.session.commit()
        return jsonify({'message': f'成功删除 {len(user_ids)} 个用户！'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量删除用户失败: {e}")
        return jsonify({'error': '批量删除失败: ' + str(e)}), 500