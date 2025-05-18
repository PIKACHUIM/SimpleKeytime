from argparse import _get_action_name
from flask import Blueprint, Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
import uuid
import os
import ssl
import random
import string
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['WTF_CSRF_ENABLED'] = False  # 是否启用CSRF跨域保护，如果你不会配置，请不要开启！！！

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 邮件SSL配置
if app.config['MAIL_USE_SSL']:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    mail.ssl_context = context

# 创建API蓝图
api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1/api')

# 数据库模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    dev_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    uid = db.Column(db.String(12), unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    is_admin = db.Column(db.Boolean, default=False)
    reset_code = db.Column(db.String(6))
    reset_code_expires = db.Column(db.DateTime)
    
    projects = db.relationship('Project', backref='owner', lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.uid:
            self.uid = self.generate_uid()
    
    def generate_uid(self):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(12))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_code(self):
        self.reset_code = ''.join(random.choice(string.digits) for _ in range(6))
        self.reset_code_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        return self.reset_code
    
    def verify_reset_code(self, code):
        if not self.reset_code or not self.reset_code_expires:
            return False
        return self.reset_code == code and datetime.utcnow() < self.reset_code_expires


class LicenseKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    activation_time = db.Column(db.DateTime)
    expiry_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    project = db.relationship('Project', back_populates='license_keys')

    def calculate_expiry(self):
        if self.activation_time and self.duration_minutes:
            return self.activation_time + timedelta(minutes=self.duration_minutes)
        return None

    def is_expired(self):
        if not self.expiry_time:
            return False
        # 统一时区处理
        expiry_time = self.expiry_time.astimezone(pytz.UTC) if self.expiry_time.tzinfo else self.expiry_time.replace(tzinfo=None)
        now = datetime.now(pytz.UTC) if self.expiry_time.tzinfo else datetime.utcnow()
        return now > expiry_time

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    latest_version = db.Column(db.String(50))
    download_url = db.Column(db.String(255))
    announcement = db.Column(db.Text)
    force_update = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(pytz.timezone('Asia/Shanghai')))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_keys = db.relationship('LicenseKey', back_populates='project', cascade='all, delete-orphan')

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class ProjectUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(50))
    signature = db.Column(db.String(200))
    avatar = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    reset_token = db.Column(db.String(64))
    reset_token_expires = db.Column(db.DateTime)
    
    project = db.relationship('Project', backref=db.backref('users', lazy=True))
    
    def __init__(self, **kwargs):
        super(ProjectUser, self).__init__(**kwargs)
        if not self.uid:
            self.uid = self.generate_uid()
    
    def generate_uid(self):
        chars = string.digits
        return ''.join([random.choice(chars) for _ in range(12)])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.reset_token
    
    def verify_reset_token(self, token):
        if not self.reset_token or not self.reset_token_expires:
            return False
        return self.reset_token == token and datetime.utcnow() < self.reset_token_expires

# 上下文处理器
@app.context_processor
def inject_globals():
    return {
        'app_name': app.config['APP_NAME'],
        'app_description': app.config['APP_DESCRIPTION'],
        'current_year': datetime.now().year,
        'masked_email': lambda email: email[:3] + '****' + email[email.find('@'):] if email else '',
        'pytz': pytz
    }

# 辅助函数
def generate_license_key(length=16):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def calculate_duration_minutes(duration_value, duration_unit):
    """将各种时间单位转换为分钟"""
    duration_value = max(1, int(duration_value))
    
    if duration_unit == 'minutes':
        return duration_value
    elif duration_unit == 'hours':
        return duration_value * 60
    elif duration_unit == 'days':
        return duration_value * 60 * 24
    elif duration_unit == 'months':
        return duration_value * 60 * 24 * 30  # 按30天算一个月
    else:
        return duration_value  # 默认按分钟

def create_default_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                email_verified=True
            )
            db.session.add(admin)
            db.session.commit()

def update_existing_users_uid():
    with app.app_context():
        users = User.query.filter_by(uid=None).all()
        for user in users:
            user.uid = user.generate_uid()
        db.session.commit()

def send_verification_email(user):
    token = user.dev_id
    verify_url = url_for('verify_email', token=token, _external=True)
    
    msg = Message(
        subject='请验证您的邮箱 - SimpleKeytime',
        recipients=[user.email],
        html=render_template('emails/verification.html', 
                           user=user, 
                           verify_url=verify_url)
    )
    
    try:
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"发送验证邮件失败: {e}")

def send_reset_code_email(user):
    reset_code = user.generate_reset_code()
    
    msg = Message(
        subject='密码重置验证码 - SimpleKeytime',
        recipients=[user.email],
        html=render_template('emails/reset_code.html',
                           user=user,
                           reset_code=reset_code)
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"发送验证码失败: {e}")
        return False

# 路由 - 认证
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login'))
        
        # 严格检查邮箱验证状态
        if not user.email_verified:
            # 重新发送验证邮件
            send_verification_email(user)
            flash('您的邮箱尚未验证，我们已重新发送验证邮件，请先验证邮箱后再登录', 'error')
            return redirect(url_for('login'))
        
        if user.email_verified:
        # 登录用户
            user.last_login = datetime.now(pytz.timezone('Asia/Shanghai'))
            user.last_login_ip = request.remote_addr
            db.session.commit()
            login_user(user, remember=remember)
            flash('登录成功', 'success')
            return redirect(url_for('dashboard_home'))
    
    return render_template('auth/login.html', forgot_password_url=url_for('reset_password_request'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_home'))
    
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, nickname=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        send_verification_email(user)
        flash('注册成功！请检查您的邮箱以完成验证', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(dev_id=token).first()
    
    if not user:
        flash('验证链接无效或已过期', 'error')
        return redirect(url_for('login'))
    
    if user.email_verified:
        flash('您的邮箱已经验证过了', 'info')
        return redirect(url_for('login'))
    
    user.email_verified = True
    db.session.commit()
    
    flash('邮箱验证成功！您现在可以登录了', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('index'))

# 密码重置功能
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            if send_reset_code_email(user):
                session['reset_email'] = email
                flash('验证码已发送到您的邮箱，请查收', 'success')
                return redirect(url_for('reset_password_verify'))
            else:
                flash('发送验证码失败，请稍后再试', 'error')
        else:
            flash('该邮箱未注册', 'error')
    
    return render_template('auth/reset_request.html')

@app.route('/reset-password/verify', methods=['GET', 'POST'])
def reset_password_verify():
    if 'reset_email' not in session:
        return redirect(url_for('reset_password_request'))
    
    email = session['reset_email']
    user = User.query.filter_by(email=email).first()
    
    if not user:
        session.pop('reset_email', None)
        return redirect(url_for('reset_password_request'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        full_email = request.form.get('full_email')
        
        if full_email != user.email:
            flash('邮箱地址不正确', 'error')
            return redirect(url_for('reset_password_verify'))
        
        if user.verify_reset_code(code):
            session['reset_verified'] = True
            return redirect(url_for('reset_password_new'))
        else:
            flash('验证码错误或已过期', 'error')
    
    return render_template('auth/reset_verify.html', masked_email=email[:3] + '****' + email[email.find('@'):])

@app.route('/reset-password/new', methods=['GET', 'POST'])
def reset_password_new():
    if 'reset_email' not in session or 'reset_verified' not in session:
        return redirect(url_for('reset_password_request'))
    
    email = session['reset_email']
    user = User.query.filter_by(email=email).first()
    
    if not user:
        session.pop('reset_email', None)
        session.pop('reset_verified', None)
        return redirect(url_for('reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('reset_password_new'))
        
        user.set_password(password)
        user.reset_code = None
        user.reset_code_expires = None
        db.session.commit()
        
        session.pop('reset_email', None)
        session.pop('reset_verified', None)
        
        flash('密码重置成功，请使用新密码登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_new.html')

# 修改密码功能
@app.route('/dashboard/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('当前密码不正确', 'error')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'error')
            return redirect(url_for('change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('密码修改成功', 'success')
        return redirect(url_for('dashboard_my'))
    
    return render_template('dashboard/change_password.html')

# 路由 - 主页面
@app.route('/')
def index():
    return render_template('index.html')

# API文档
@app.route('/v1/api/doc')
@login_required
def apidoc():
    return render_template('pages/api_docs.html')

# 路由 - 控制台
@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('dashboard_home'))

@app.route('/dashboard/home')
@login_required
def dashboard_home():
    announcements = Announcement.query.filter_by(is_active=True)\
                                    .order_by(Announcement.created_at.desc())\
                                    .limit(5).all()
    projects_count = Project.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard/home.html',
                         announcements=announcements,
                         projects_count=projects_count,
                         user=current_user)

@app.route('/dashboard/projects', methods=['GET', 'POST'])
@login_required
def dashboard_projects():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            try:
                name = request.form.get('name').strip()
                description = request.form.get('description', '').strip()
                
                if not name:
                    flash('项目名称不能为空', 'error')
                    return redirect(url_for('dashboard_projects'))
                
                project = Project(
                    name=name,
                    description=description if description else None,
                    user_id=current_user.id
                )
                db.session.add(project)
                db.session.commit()
                flash('项目创建成功', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'创建项目失败: {str(e)}')
                flash('创建项目失败，请稍后再试', 'error')
        
        elif action == 'delete':
            try:
                project_id = request.form.get('project_id')
                project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
                
                if project:
                    db.session.delete(project)
                    db.session.commit()
                    flash('项目已删除', 'success')
                else:
                    flash('项目不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'删除项目失败: {str(e)}')
                flash('删除项目失败，请稍后再试', 'error')
        
        elif action == 'update':
            try:
                project_id = request.form.get('project_id')
                project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
                
                if project:
                    project.name = request.form.get('name').strip()
                    project.description = request.form.get('description', '').strip() or None
                    project.latest_version = request.form.get('latest_version', '').strip() or None
                    project.download_url = request.form.get('download_url', '').strip() or None
                    project.announcement = request.form.get('announcement', '').strip() or None
                    project.force_update = request.form.get('force_update') == 'on'
                    project.updated_at = datetime.utcnow()
                    
                    db.session.commit()
                    flash('项目更新成功', 'success')
                else:
                    flash('项目不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'更新项目失败: {str(e)}')
                flash('更新项目失败，请稍后再试', 'error')
        
        return redirect(url_for('dashboard_projects'))
    
    projects = Project.query.filter_by(user_id=current_user.id)\
                          .order_by(Project.updated_at.desc())\
                          .all()

    return render_template('dashboard/projects.html', projects=projects, user=current_user)

@app.route('/dashboard/my', methods=['GET', 'POST'])
@login_required
def dashboard_my():
    if request.method == 'POST':
        try:
            current_user.nickname = request.form.get('nickname', '').strip() or None
            
            if 'avatar' in request.files:
                avatar = request.files['avatar']
                if avatar.filename != '':
                    filename = f"avatar_{current_user.id}_{int(datetime.now().timestamp())}.{avatar.filename.split('.')[-1]}"
                    upload_path = os.path.join(app.root_path, 'static', 'uploads')
                    os.makedirs(upload_path, exist_ok=True)
                    avatar.save(os.path.join(upload_path, filename))
                    current_user.avatar = f"/static/uploads/{filename}"
            
            db.session.commit()
            flash('个人信息已更新', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'更新个人信息失败: {str(e)}')
            flash('更新失败，请稍后再试', 'error')
        
        return redirect(url_for('dashboard_my'))
    
    return render_template('dashboard/my.html', user=current_user)

@app.route('/dashboard/reset-dev-id', methods=['POST'])
@login_required
def reset_dev_id():
    try:
        # 生成新的DevID
        new_dev_id = str(uuid.uuid4())
        current_user.dev_id = new_dev_id
        current_user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 返回包含新DevID的JSON响应
        return jsonify({
            'status': 'success',
            'message': '开发者ID已重置',
            'new_dev_id': new_dev_id
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'重置开发者ID失败: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': '重置失败，请稍后再试'
        }), 500

# 新增API路由获取项目数据
@app.route('/api/projects/<int:project_id>')
@login_required
def get_project_data(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'latest_version': project.latest_version,
        'download_url': project.download_url,
        'announcement': project.announcement,
        'force_update': project.force_update
    })

# 卡密管理路由
@app.route('/dashboard/licenses', methods=['GET', 'POST'])
@login_required
def dashboard_licenses():
    def get_beijing_time():
        return datetime.now(pytz.timezone('Asia/Shanghai'))

    # 获取用户所有项目
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        project_id = None
        
        # 批量操作处理
        if action == 'batch_action':
            try:
                selected_ids = request.form.get('selected_licenses', '').split(',')
                selected_ids = [int(id) for id in selected_ids if id]
                
                if not selected_ids:
                    flash('请至少选择一个卡密', 'error')
                    return redirect(request.referrer or url_for('dashboard_licenses'))
                
                batch_action = request.form.get('batch_action_type')
                
                if not selected_ids:
                    flash('请至少选择一个卡密', 'error')
                    return redirect(url_for('dashboard_licenses'))
                
                licenses = LicenseKey.query.join(Project)\
                    .filter(
                        LicenseKey.id.in_(selected_ids),
                        Project.user_id == current_user.id
                    ).all()
                
                for license in licenses:
                    if batch_action == 'activate':
                        license.is_active = True
                        license.is_banned = False
                    elif batch_action == 'deactivate':
                        license.is_active = False
                    elif batch_action == 'ban':
                        license.is_banned = True
                        license.is_active = False
                    elif batch_action == 'unban':
                        license.is_banned = False
                    elif batch_action == 'delete':
                        db.session.delete(license)
                
                db.session.commit()
                flash(f'成功{get_action_name(batch_action)} {len(licenses)} 个卡密', 'success')
                return redirect(url_for('dashboard_licenses'))
            
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'批量操作失败: {str(e)}')
                flash('批量操作失败', 'error')
        
        # 单个卡密编辑
        elif action == 'edit_license':
            try:
                key_id = request.form.get('key_id')
                license_key = LicenseKey.query.join(Project)\
                    .filter(
                        LicenseKey.id == key_id,
                        Project.user_id == current_user.id
                    ).first()
                
                if license_key:
                    # 更新卡密信息
                    duration_value = int(request.form.get('duration_value', 1))
                    duration_unit = request.form.get('duration_unit', 'days')
                    license_key.duration_minutes = calculate_duration_minutes(duration_value, duration_unit)
                    license_key.notes = request.form.get('notes', '').strip() or None
                    license_key.is_active = request.form.get('is_active') == 'on'
                    license_key.is_banned = request.form.get('is_banned') == 'on'
                    
                    if license_key.is_banned:
                        license_key.is_active = False
                    
                    # 重新计算过期时间
                    if license_key.activation_time and license_key.is_active:
                        license_key.expiry_time = license_key.calculate_expiry()
                    
                    db.session.commit()
                    flash('卡密信息已更新', 'success')
                    project_id = license_key.project_id
                else:
                    flash('卡密不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'更新卡密失败: {str(e)}')
                flash('更新卡密失败', 'error')
        
        elif action == 'create':
            try:
                project_id = request.form.get('project_id')
                quantity = int(request.form.get('quantity', 1))
                duration_value = int(request.form.get('duration_value', 1))
                duration_unit = request.form.get('duration_unit', 'days')
                notes = request.form.get('notes', '').strip()
                
                project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
                if not project:
                    flash('项目不存在或无权操作', 'error')
                    return redirect(url_for('dashboard_licenses'))
                
                duration_minutes = calculate_duration_minutes(duration_value, duration_unit)
                
                new_keys = []
                for _ in range(quantity):
                    key = LicenseKey(
                        key=generate_license_key(),
                        project_id=project.id,
                        duration_minutes=duration_minutes,
                        notes=notes if notes else None,
                        created_at=get_beijing_time()
                    )
                    new_keys.append(key)
                    db.session.add(key)
                
                db.session.commit()
                flash(f'成功生成 {quantity} 个卡密', 'success')
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'生成卡密失败: {str(e)}')
                flash('生成卡密失败，请稍后再试', 'error')
        
        elif action in ['toggle_active', 'ban', 'unban', 'activate', 'deactivate']:
            try:
                key_id = request.form.get('key_id')
                license_key = LicenseKey.query.join(Project)\
                    .filter(
                        LicenseKey.id == key_id,
                        Project.user_id == current_user.id
                    ).first()
                
                if license_key:
                    if action == 'toggle_active':
                        license_key.is_active = not license_key.is_active
                        status = "激活" if license_key.is_active else "停用"
                        flash(f'卡密已{status}', 'success')
                    elif action == 'ban':
                        license_key.is_banned = True
                        license_key.is_active = False
                        flash('卡密已封禁', 'success')
                    elif action == 'unban':
                        license_key.is_banned = False
                        flash('卡密已解封', 'success')
                    elif action == 'activate':
                        license_key.activation_time = get_beijing_time()
                        license_key.expiry_time = license_key.calculate_expiry()
                        license_key.is_active = True
                        flash('卡密已手动激活', 'success')
                    elif action == 'deactivate':
                        license_key.activation_time = None
                        license_key.expiry_time = None
                        flash('卡密已取消激活', 'success')
                    
                    project_id = license_key.project_id
                    db.session.commit()
                else:
                    flash('卡密不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'操作失败: {str(e)}')
                flash('操作失败', 'error')
        
        elif action == 'delete':
            try:
                key_id = request.form.get('key_id')
                license_key = LicenseKey.query.join(Project)\
                    .filter(
                        LicenseKey.id == key_id,
                        Project.user_id == current_user.id
                    ).first()
                
                if license_key:
                    project_id = license_key.project_id
                    db.session.delete(license_key)
                    db.session.commit()
                    flash('卡密已删除', 'success')
                else:
                    flash('卡密不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'删除卡密失败: {str(e)}')
                flash('删除卡密失败', 'error')
        
        # 检查并更新过期状态
        expired_keys = LicenseKey.query.join(Project)\
            .filter(
                LicenseKey.expiry_time < get_beijing_time(),
                LicenseKey.is_active == True,
                Project.user_id == current_user.id
            ).all()
        
        for key in expired_keys:
            key.is_active = False
        if expired_keys:
            db.session.commit()
        
        if project_id:
            return redirect(url_for('dashboard_licenses'))
        return redirect(url_for('dashboard_licenses'))
    
    # GET请求处理
    project_id = request.args.get('project_id')
    selected_project = None
    
    # 获取卡密列表
    query = LicenseKey.query.join(Project).filter(Project.user_id == current_user.id)
    
    if project_id:
        try:
            project_id = int(project_id)
            selected_project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
            if selected_project:
                query = query.filter(LicenseKey.project_id == project_id)
        except ValueError:
            pass
    
    licenses = query.order_by(LicenseKey.created_at.desc()).all()
    
    # 转换时间为北京时间
    for license in licenses:
        if license.created_at:
            license.created_at = license.created_at.astimezone(pytz.timezone('Asia/Shanghai'))
        if license.activation_time:
            license.activation_time = license.activation_time.astimezone(pytz.timezone('Asia/Shanghai'))
        if license.expiry_time:
            license.expiry_time = license.expiry_time.astimezone(pytz.timezone('Asia/Shanghai'))
    
    return render_template('dashboard/licenses.html', 
                         projects=projects,
                         licenses=licenses,
                         selected_project_id=project_id if selected_project else None)

def get_action_name(action_type):
    return {
        'activate': '激活',
        'deactivate': '停用',
        'ban': '封禁',
        'unban': '解封',
        'delete': '删除'
    }.get(action_type, '操作')

# 卡密编辑API
@app.route('/api/license/<int:license_id>', methods=['GET'])
@login_required
def get_license_details(license_id):
    license = LicenseKey.query.join(Project)\
        .filter(
            LicenseKey.id == license_id,
            Project.user_id == current_user.id
        ).first_or_404()
    
    return jsonify({
        'id': license.id,
        'key': license.key,
        'duration_minutes': license.duration_minutes,
        'notes': license.notes,
        'is_active': license.is_active,
        'is_banned': license.is_banned,
        'activation_time': license.activation_time.isoformat() if license.activation_time else None,
        'expiry_time': license.expiry_time.isoformat() if license.expiry_time else None
    })


# 卡密激活API
@app.route('/api/license/activate', methods=['POST'])
def activate_license():
    data = request.get_json()
    key = data.get('key')
    app_id = data.get('app_id')
    
    if not key or not app_id:
        return jsonify({'status': 'error', 'message': '参数不完整'}), 400
    
    license_key = LicenseKey.query.join(Project)\
        .filter(
            LicenseKey.key == key,
            Project.app_id == app_id
        ).first()
    
    if not license_key:
        return jsonify({'status': 'error', 'message': '卡密无效'}), 404
    
    if license_key.is_banned:
        return jsonify({'status': 'error', 'message': '卡密已被封禁'}), 403
    
    if not license_key.is_active:
        return jsonify({'status': 'error', 'message': '卡密未激活'}), 403
    
    if license_key.activation_time:
        if license_key.is_expired():
            return jsonify({'status': 'error', 'message': '卡密已过期'}), 403
        return jsonify({'status': 'error', 'message': '卡密已被使用'}), 403
    
    # 激活卡密
    license_key.activation_time = datetime.utcnow()
    license_key.expiry_time = license_key.calculate_expiry()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'expiry_time': license_key.expiry_time.isoformat(),
        'duration_minutes': license_key.duration_minutes
    })

# 项目用户管理路由
# 项目用户管理路由
@app.route('/dashboard/project-users', methods=['GET', 'POST'])
@login_required
def dashboard_project_users():
    project_id = request.args.get('project_id')
    
    if not project_id and request.method == 'POST':
        project_id = request.form.get('project_id')
    
    if not project_id:
        flash('请从项目列表中选择一个项目', 'info')
        return redirect(url_for('dashboard_projects'))
    
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        flash('项目不存在或无权访问', 'error')
        return redirect(url_for('dashboard_projects'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            try:
                username = request.form.get('username').strip()
                email = request.form.get('email').strip()
                nickname = request.form.get('nickname', '').strip()
                signature = request.form.get('signature', '').strip()
                password = request.form.get('password')
                
                if not password:
                    password = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(12)])
                
                if ProjectUser.query.filter_by(project_id=project.id, username=username).first():
                    flash('用户名已存在', 'error')
                    return redirect(url_for('dashboard_project_users', project_id=project.id))
                
                if ProjectUser.query.filter_by(project_id=project.id, email=email).first():
                    flash('邮箱已被使用', 'error')
                    return redirect(url_for('dashboard_project_users', project_id=project.id))
                
                user = ProjectUser(
                    project_id=project.id,
                    username=username,
                    email=email,
                    nickname=nickname if nickname else None,
                    signature=signature if signature else None,
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                
                flash(f'用户创建成功，初始密码: {password}', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'创建用户失败: {str(e)}')
                flash('创建用户失败，请稍后再试', 'error')
        
        elif action == 'edit':
            try:
                user_id = request.form.get('user_id')
                user = ProjectUser.query.filter_by(id=user_id, project_id=project.id).first()
                
                if user:
                    user.username = request.form.get('username').strip()
                    user.email = request.form.get('email').strip()
                    user.nickname = request.form.get('nickname', '').strip() or None
                    user.signature = request.form.get('signature', '').strip() or None
                    
                    new_password = request.form.get('password')
                    if new_password:
                        user.set_password(new_password)
                    
                    db.session.commit()
                    flash('用户信息已更新', 'success')
                else:
                    flash('用户不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'更新用户失败: {str(e)}')
                flash('更新用户失败', 'error')
        
        elif action == 'toggle_ban':
            try:
                user_id = request.form.get('user_id')
                user = ProjectUser.query.filter_by(id=user_id, project_id=project.id).first()
                
                if user:
                    user.is_banned = not user.is_banned
                    user.is_active = not user.is_banned
                    db.session.commit()
                    flash(f'用户已{"封禁" if user.is_banned else "解封"}', 'success')
                else:
                    flash('用户不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'操作失败: {str(e)}')
                flash('操作失败', 'error')
        
        elif action == 'delete':
            try:
                user_id = request.form.get('user_id')
                user = ProjectUser.query.filter_by(id=user_id, project_id=project.id).first()
                
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    flash('用户已删除', 'success')
                else:
                    flash('用户不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'删除用户失败: {str(e)}')
                flash('删除用户失败', 'error')
        
        elif action == 'send_reset_email':
            try:
                user_id = request.form.get('user_id')
                user = ProjectUser.query.filter_by(id=user_id, project_id=project.id).first()
                
                if user:
                    send_project_user_reset_email(user, project)
                    flash('重置密码邮件已发送', 'success')
                else:
                    flash('用户不存在或无权操作', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'发送重置邮件失败: {str(e)}')
                flash('发送重置邮件失败', 'error')
        
        return redirect(url_for('dashboard_project_users', project_id=project.id))
    
    users = ProjectUser.query.filter_by(project_id=project.id)\
                          .order_by(ProjectUser.created_at.desc())\
                          .all()
    
    return render_template('dashboard/project_users.html', 
                         project=project,
                         users=users)

# 项目用户API
@app.route('/api/project-users/<int:user_id>')
@login_required
def get_project_user(user_id):
    user = ProjectUser.query.join(Project)\
        .filter(
            ProjectUser.id == user_id,
            Project.user_id == current_user.id
        ).first_or_404()
    
    return jsonify({
        'id': user.id,
        'uid': user.uid,
        'username': user.username,
        'email': user.email,
        'nickname': user.nickname,
        'signature': user.signature,
        'is_active': user.is_active,
        'is_banned': user.is_banned
    })

# 项目用户密码重置路由
@app.route('/project-user-reset', methods=['GET', 'POST'])
def project_user_reset():
    token = request.args.get('token')
    
    if not token:
        flash('无效的重置链接', 'error')
        return redirect(url_for('index'))
    
    user = ProjectUser.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('重置链接无效或已过期', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get(user.project_id)
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('project_user_reset', token=token))
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        flash('密码重置成功', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/project_user_reset.html', 
                         project=project,
                         user=user)

# 发送项目用户重置密码邮件
def send_project_user_reset_email(user, project):
    reset_token = user.generate_reset_token()
    reset_url = url_for('project_user_reset', token=reset_token, _external=True)
    
    msg = Message(
        subject=f'重置您的{project.name}账户密码',
        recipients=[user.email],
        html=render_template('emails/project_user_reset.html', 
                          user=user, 
                          project=project,
                          reset_url=reset_url)
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"发送重置邮件失败: {e}")
        return False

@api_v1.route('/projects/<app_id>', methods=['GET'])
def get_project_info(app_id):
    """
    获取项目完整信息API
    ---
    tags:
      - 项目管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
    responses:
      200:
        description: 项目完整信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                name:
                  type: string
                  example: 我的项目
                created_at:
                  type: string
                  format: date-time
                  example: "2023-01-01T00:00:00"
                alldata:
                  type: object
                  properties:
                    latestVersion:
                      type: string
                      example: 1.0.0
                    updateUrl:
                      type: string
                      example: https://example.com/download/latest
                    updateNotice:
                      type: string
                      example: 重要更新说明
                    ifForce:
                      type: boolean
                      example: false
      404:
        description: 项目不存在
    """
    return get_project_data(app_id, full_data=True)

@api_v1.route('/projects/<app_id>/latestVersion', methods=['GET'])
def get_latest_version(app_id):
    """
    获取项目最新版本
    ---
    tags:
      - 项目管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
    responses:
      200:
        description: 最新版本信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: string
              example: 1.0.0
      404:
        description: 项目不存在
    """
    return get_project_data(app_id, field='latest_version')

@api_v1.route('/projects/<app_id>/updateUrl', methods=['GET'])
def get_update_url(app_id):
    """
    获取项目更新URL
    ---
    tags:
      - 项目管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
    responses:
      200:
        description: 更新URL
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: string
              example: https://example.com/download/latest
      404:
        description: 项目不存在
    """
    return get_project_data(app_id, field='download_url')

@api_v1.route('/projects/<app_id>/updateNotice', methods=['GET'])
def get_update_notice(app_id):
    """
    获取项目更新公告
    ---
    tags:
      - 项目管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
    responses:
      200:
        description: 更新公告
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: string
              example: 重要更新说明
      404:
        description: 项目不存在
    """
    return get_project_data(app_id, field='announcement')

@api_v1.route('/projects/<app_id>/ifForce', methods=['GET'])
def get_if_force(app_id):
    """
    获取项目是否强制更新
    ---
    tags:
      - 项目管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
    responses:
      200:
        description: 是否强制更新
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: boolean
              example: false
      404:
        description: 项目不存在
    """
    return get_project_data(app_id, field='force_update')

def get_project_data(app_id, full_data=False, field=None):
    """
    获取项目数据的通用函数
    """
    try:
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
        
        if full_data:
            response_data = {
                'status': 'success',
                'data': {
                    'name': project.name,
                    'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'alldata': {
                        'latestVersion': project.latest_version or '',
                        'updateUrl': project.download_url or '',
                        'updateNotice': project.announcement or '',
                        'ifForce': project.force_update or False
                    }
                }
            }
        elif field:
            # 获取单个字段的值
            value = getattr(project, field)
            if value is None:
                value = '' if field != 'force_update' else False
            response_data = {
                'status': 'success',
                'data': value
            }
        
        return jsonify(response_data)
    
    except Exception as e:
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
@api_v1.route('/licenses/<app_id>/status', methods=['GET'])
def get_license_status(app_id):
    """
    获取卡密状态API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
    responses:
      200:
        description: 卡密状态信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: string
              example: 可用
      404:
        description: 项目不存在
    """
    try:
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': 'available'  # This would be more detailed in a real implementation
        })
    except Exception as e:
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/alldata', methods=['GET'])
def get_license_all_data(app_id):
    """
    获取卡密完整信息API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: query
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: query
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 卡密完整信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                status:
                  type: string
                  example: 已激活
                key:
                  type: string
                  example: ABC123DEF456
                created_at:
                  type: string
                  format: date-time
                  example: "2023-01-01T00:00:00"
                duration_minutes:
                  type: integer
                  example: 1440
                project_name:
                  type: string
                  example: 我的项目
                activation_time:
                  type: string
                  format: date-time
                  example: "2023-01-02T00:00:00"
                expiry_time:
                  type: string
                  format: date-time
                  example: "2023-01-03T00:00:00"
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.args.get('dev_id')
        key = request.args.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Determine status
        if license_key.is_banned:
            status = '已封禁'
        elif not license_key.is_active:
            status = '已禁用'
        elif license_key.activation_time:
            if license_key.is_expired():
                status = '已过期'
            else:
                status = '已激活'
        else:
            status = '可用'
        
        return jsonify({
            'status': 'success',
            'data': {
                'status': status,
                'key': license_key.key,
                'created_at': license_key.created_at.isoformat(),
                'duration_minutes': license_key.duration_minutes,
                'project_name': project.name,
                'activation_time': license_key.activation_time.isoformat() if license_key.activation_time else None,
                'expiry_time': license_key.expiry_time.isoformat() if license_key.expiry_time else None
            }
        })
    except Exception as e:
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/activate', methods=['POST'])
def activate_license_key(app_id):
    """
    激活卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 卡密激活结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                duration_minutes:
                  type: integer
                  example: 1440
                expiry_time:
                  type: string
                  format: date-time
                  example: "2023-01-03T00:00:00"
                project_name:
                  type: string
                  example: 我的项目
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问或卡密不可用
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Check if license can be activated
        if license_key.is_banned or not license_key.is_active or license_key.activation_time:
            return jsonify({
                'status': 'error',
                'message': 'License key cannot be activated'
            }), 403
        
        # Activate license
        license_key.activation_time = datetime.utcnow()
        license_key.expiry_time = license_key.calculate_expiry()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'duration_minutes': license_key.duration_minutes,
                'expiry_time': license_key.expiry_time.isoformat(),
                'project_name': project.name
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/deactivate', methods=['POST'])
def deactivate_license_key(app_id):
    """
    取消激活卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 取消激活结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                duration_minutes:
                  type: integer
                  example: 1440
                project_name:
                  type: string
                  example: 我的项目
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Deactivate license
        license_key.activation_time = None
        license_key.expiry_time = None
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'duration_minutes': license_key.duration_minutes,
                'project_name': project.name
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/delete', methods=['POST'])
def delete_license_key(app_id):
    """
    删除卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 删除结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                key:
                  type: string
                  example: ABC123DEF456
                project_name:
                  type: string
                  example: 我的项目
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Delete license
        db.session.delete(license_key)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'key': key,
                'project_name': project.name
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/disable', methods=['POST'])
def disable_license_key(app_id):
    """
    禁用卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 禁用结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                key:
                  type: string
                  example: ABC123DEF456
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Disable license
        license_key.is_active = False
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'key': key
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/enable', methods=['POST'])
def enable_license_key(app_id):
    """
    启用卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 启用结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                key:
                  type: string
                  example: ABC123DEF456
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Enable license (can't enable if banned)
        if license_key.is_banned:
            return jsonify({
                'status': 'error',
                'message': 'Cannot enable a banned license'
            }), 403
            
        license_key.is_active = True
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'key': key
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/ban', methods=['POST'])
def ban_license_key(app_id):
    """
    封禁卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 封禁结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                key:
                  type: string
                  example: ABC123DEF456
                project_name:
                  type: string
                  example: 我的项目
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Ban license
        license_key.is_banned = True
        license_key.is_active = False
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'key': key,
                'project_name': project.name
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/licenses/<app_id>/unban', methods=['POST'])
def unban_license_key(app_id):
    """
    解封卡密API
    ---
    tags:
      - 卡密管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: key
        in: formData
        type: string
        required: true
        description: 卡密
    responses:
      200:
        description: 解封结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                key:
                  type: string
                  example: ABC123DEF456
                project_name:
                  type: string
                  example: 我的项目
      404:
        description: 项目或卡密不存在
      403:
        description: 无权限访问
    """
    try:
        dev_id = request.form.get('dev_id')
        key = request.form.get('key')
        
        if not dev_id or not key:
            return jsonify({
                'status': 'error',
                'message': 'Missing dev_id or key parameter'
            }), 400
        
        # Verify project ownership
        project = Project.query.filter_by(app_id=app_id).first()
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        if project.owner.dev_id != dev_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        # Get license key
        license_key = LicenseKey.query.filter_by(
            key=key,
            project_id=project.id
        ).first()
        
        if not license_key:
            return jsonify({
                'status': 'error',
                'message': 'License key not found'
            }), 404
        
        # Unban license
        license_key.is_banned = False
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'key': key,
                'project_name': project.name
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@api_v1.route('/project-users/<app_id>/ifRegister', methods=['GET'])
def check_user_registration(app_id):
    """
    检查用户注册状态API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: username
        in: query
        type: string
        description: 用户名
      - name: uid
        in: query
        type: string
        description: 用户UID
      - name: email
        in: query
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 用户注册状态
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: string
              example: 已注册
      400:
        description: 参数错误
      404:
        description: 用户未找到
    """
    username = request.args.get('username')
    uid = request.args.get('uid')
    email = request.args.get('email')
    
    if not (username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'success',
            'data': '未找到'
        })
    
    if not user.is_active:
        return jsonify({
            'status': 'success',
            'data': '邮箱未验证'
        })
    
    return jsonify({
        'status': 'success',
        'data': '已注册'
    })

@api_v1.route('/project-users/<app_id>/alldata', methods=['GET'])
def get_user_all_data(app_id):
    """
    获取用户完整信息API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: query
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: query
        type: integer
        description: 用户ID
      - name: username
        in: query
        type: string
        description: 用户名
      - name: uid
        in: query
        type: string
        description: 用户UID
      - name: email
        in: query
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 用户完整信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                uid:
                  type: string
                  example: "123456789012"
                username:
                  type: string
                  example: "testuser"
                email:
                  type: string
                  example: "user@example.com"
                nickname:
                  type: string
                  example: "测试用户"
                signature:
                  type: string
                  example: "个性签名"
                avatar:
                  type: string
                  example: "/static/uploads/avatar.jpg"
                is_active:
                  type: boolean
                  example: true
                is_banned:
                  type: boolean
                  example: false
                created_at:
                  type: string
                  format: date-time
                  example: "2023-01-01T00:00:00"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.args.get('dev_id')
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    uid = request.args.get('uid')
    email = request.args.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': user.id,
            'uid': user.uid,
            'username': user.username,
            'email': user.email,
            'nickname': user.nickname,
            'signature': user.signature,
            'avatar': user.avatar,
            'is_active': user.is_active,
            'is_banned': user.is_banned,
            'created_at': user.created_at.isoformat()
        }
    })

@api_v1.route('/project-users/<app_id>/registerDate', methods=['GET'])
def get_user_register_date(app_id):
    """
    获取用户注册日期API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: query
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: query
        type: integer
        description: 用户ID
      - name: username
        in: query
        type: string
        description: 用户名
      - name: uid
        in: query
        type: string
        description: 用户UID
      - name: email
        in: query
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 用户注册日期
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: string
              format: date-time
              example: "2023-01-01T00:00:00"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.args.get('dev_id')
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    uid = request.args.get('uid')
    email = request.args.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': user.created_at.isoformat()
    })

@api_v1.route('/project-users/<app_id>/lastLogin', methods=['GET'])
def get_user_last_login(app_id):
    """
    获取用户最后登录信息API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: query
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: query
        type: integer
        description: 用户ID
      - name: username
        in: query
        type: string
        description: 用户名
      - name: uid
        in: query
        type: string
        description: 用户UID
      - name: email
        in: query
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 用户最后登录信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                last_login:
                  type: string
                  format: date-time
                  example: "2023-01-01T00:00:00"
                last_login_ip:
                  type: string
                  example: "127.0.0.1"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.args.get('dev_id')
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    uid = request.args.get('uid')
    email = request.args.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'last_login_ip': user.last_login_ip
        }
    })

@api_v1.route('/project-users/<app_id>/ban', methods=['POST'])
def ban_user(app_id):
    """
    封禁用户API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: formData
        type: integer
        description: 用户ID
      - name: username
        in: formData
        type: string
        description: 用户名
      - name: uid
        in: formData
        type: string
        description: 用户UID
      - name: email
        in: formData
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 封禁结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                username:
                  type: string
                  example: "testuser"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.form.get('dev_id')
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    uid = request.form.get('uid')
    email = request.form.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    try:
        user.is_banned = True
        user.is_active = False
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'username': user.username
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"封禁用户失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '封禁用户失败'
        }), 500

@api_v1.route('/project-users/<app_id>/unban', methods=['POST'])
def unban_user(app_id):
    """
    解封用户API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: formData
        type: integer
        description: 用户ID
      - name: username
        in: formData
        type: string
        description: 用户名
      - name: uid
        in: formData
        type: string
        description: 用户UID
      - name: email
        in: formData
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 解封结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                username:
                  type: string
                  example: "testuser"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.form.get('dev_id')
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    uid = request.form.get('uid')
    email = request.form.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    try:
        user.is_banned = False
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'username': user.username
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"解封用户失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '解封用户失败'
        }), 500

@api_v1.route('/project-users/<app_id>/delete', methods=['POST'])
def delete_user(app_id):
    """
    删除用户API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: formData
        type: integer
        description: 用户ID
      - name: username
        in: formData
        type: string
        description: 用户名
      - name: uid
        in: formData
        type: string
        description: 用户UID
      - name: email
        in: formData
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 删除结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                username:
                  type: string
                  example: "testuser"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.form.get('dev_id')
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    uid = request.form.get('uid')
    email = request.form.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'username': username
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除用户失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '删除用户失败'
        }), 500

@api_v1.route('/project-users/<app_id>/sendReset', methods=['POST'])
def send_reset_email(app_id):
    """
    发送密码重置邮件API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: dev_id
        in: formData
        type: string
        required: true
        description: 开发者DevID
      - name: user_id
        in: formData
        type: integer
        description: 用户ID
      - name: username
        in: formData
        type: string
        description: 用户名
      - name: uid
        in: formData
        type: string
        description: 用户UID
      - name: email
        in: formData
        type: string
        description: 用户邮箱
    responses:
      200:
        description: 发送结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                email:
                  type: string
                  example: "user@example.com"
      400:
        description: 参数错误
      403:
        description: 无权限访问
      404:
        description: 用户未找到
    """
    dev_id = request.form.get('dev_id')
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    uid = request.form.get('uid')
    email = request.form.get('email')
    
    if not dev_id:
        return jsonify({
            'status': 'error',
            'message': '必须提供dev_id'
        }), 400
    
    if not (user_id or username or uid or email):
        return jsonify({
            'status': 'error',
            'message': '必须提供user_id、username、uid或email中的一个参数'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    if project.owner.dev_id != dev_id:
        return jsonify({
            'status': 'error',
            'message': '无权限访问'
        }), 403
    
    query = ProjectUser.query.filter_by(project_id=project.id)
    
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif username:
        user = query.filter_by(username=username).first()
    elif uid:
        user = query.filter_by(uid=uid).first()
    else:
        user = query.filter_by(email=email).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    try:
        if send_project_user_reset_email(user, project):
            return jsonify({
                'status': 'success',
                'data': {
                    'success': True,
                    'email': user.email
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '发送重置邮件失败'
            }), 500
    except Exception as e:
        app.logger.error(f"发送重置邮件失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '发送重置邮件失败'
        }), 500

@api_v1.route('/project-users/<app_id>/login', methods=['POST'])
def user_login(app_id):
    """
    用户登录API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: username
        in: formData
        type: string
        required: true
        description: 用户名
      - name: password
        in: formData
        type: string
        required: true
        description: 密码
    responses:
      200:
        description: 登录结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                user_id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "testuser"
                last_login:
                  type: string
                  format: date-time
                  example: "2023-01-01T00:00:00"
                last_login_ip:
                  type: string
                  example: "127.0.0.1"
      400:
        description: 参数错误
      401:
        description: 认证失败
      403:
        description: 用户被封禁
      404:
        description: 用户未找到
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({
            'status': 'error',
            'message': '必须提供username和password'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    user = ProjectUser.query.filter_by(
        project_id=project.id,
        username=username
    ).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户未找到'
        }), 404
    
    if user.is_banned:
        return jsonify({
            'status': 'error',
            'message': '用户已被封禁'
        }), 403
    
    if not user.check_password(password):
        return jsonify({
            'status': 'error',
            'message': '用户名或密码错误'
        }), 401
    
    try:
        # 更新最后登录信息
        user.last_login = datetime.utcnow()
        user.last_login_ip = request.remote_addr
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'last_login': user.last_login.isoformat(),
                'last_login_ip': user.last_login_ip
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"登录失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '登录失败'
        }), 500

@api_v1.route('/project-users/<app_id>/register', methods=['POST'])
def user_register(app_id):
    """
    用户注册API
    ---
    tags:
      - 用户管理
    parameters:
      - name: app_id
        in: path
        type: string
        required: true
        description: 项目AppID
      - name: username
        in: formData
        type: string
        required: true
        description: 用户名
      - name: email
        in: formData
        type: string
        required: true
        description: 邮箱
      - name: password
        in: formData
        type: string
        required: true
        description: 密码
      - name: nickname
        in: formData
        type: string
        description: 昵称
      - name: signature
        in: formData
        type: string
        description: 个性签名
    responses:
      200:
        description: 注册结果
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                user_id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "testuser"
                email:
                  type: string
                  example: "user@example.com"
      400:
        description: 参数错误
      409:
        description: 用户名或邮箱已存在
    """
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    signature = request.form.get('signature')
    
    if not username or not email or not password:
        return jsonify({
            'status': 'error',
            'message': '必须提供username、email和password'
        }), 400
    
    project = Project.query.filter_by(app_id=app_id).first()
    if not project:
        return jsonify({
            'status': 'error',
            'message': '项目不存在'
        }), 404
    
    # 检查用户名和邮箱是否已存在
    if ProjectUser.query.filter_by(project_id=project.id, username=username).first():
        return jsonify({
            'status': 'error',
            'message': '用户名已存在'
        }), 409
    
    if ProjectUser.query.filter_by(project_id=project.id, email=email).first():
        return jsonify({
            'status': 'error',
            'message': '邮箱已被使用'
        }), 409
    
    try:
        user = ProjectUser(
            project_id=project.id,
            username=username,
            email=email,
            nickname=nickname if nickname else None,
            signature=signature if signature else None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # 发送激活邮件
        send_project_user_reset_email(user, project)
        
        return jsonify({
            'status': 'success',
            'data': {
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"注册失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '注册失败'
        }), 500

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# 用户加载器
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
        update_existing_users_uid()
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)
    app.register_blueprint(api_v1)
    app.run(debug=True, port=Config.APP_PORT)