from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import os
import ssl
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = '5f4dcc3b5aa765d61d8327deb882cf99b7b2b3c1b3f5e5e9c8d7a6b5c4d3e2f1'

# 初始化 Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
csrf = CSRFProtect(app)  # 启用CSRF保护

if app.config['MAIL_USE_SSL']:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    mail.ssl_context = context

# 数据库模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    dev_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    uid = db.Column(db.String(12), unique=True)  # 新增12位UID字段
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))  # 新增IP字段
    is_admin = db.Column(db.Boolean, default=False)
    
    projects = db.relationship('Project', backref='owner', lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.uid:
            self.uid = self.generate_uid()
    
    def generate_uid(self):
        import random
        import string
        # 生成12位数字字母混合UID
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(12))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    latest_version = db.Column(db.String(50))
    download_url = db.Column(db.String(255))
    announcement = db.Column(db.Text)
    force_update = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

def create_default_admin():
    with app.app_context():
        # 检查admin是否已存在
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建默认管理员
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),  # 默认密码
                is_admin=True,
                email_verified=True,
                uid="000000000001"
            )
            db.session.add(admin)
            db.session.commit()
            print("默认管理员账户已创建: admin/admin123")

# 上下文处理器 - 使变量在所有模板中可用
@app.context_processor
def inject_globals():
    return {
        'app_name': app.config['APP_NAME'],
        'app_description': app.config['APP_DESCRIPTION'],
        'current_year': datetime.now().year
    }

# 路由 - 主页
@app.route('/')
def index():
    return render_template('index.html')

# 路由 - 认证
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login'))
        
        if not user.email_verified:
            flash('您的邮箱尚未验证，请先验证邮箱后再登录', 'error')
            return redirect(url_for('login'))
        
        # 更新登录时间和IP
        user.last_login = datetime.utcnow()
        user.last_login_ip = request.remote_addr  # 记录IP
        db.session.commit()
        
        login_user(user, remember=remember)
        flash('登录成功', 'success')
        return redirect(url_for('dashboard_home'))
    
    return render_template('auth/login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return redirect(url_for('register'))
        
        # 创建用户
        user = User(username=username, email=email, nickname=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # 发送验证邮件
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
    session.clear()
    flash('您已成功登出', 'success')
    return redirect(url_for('index'))

# 路由 - 控制台
@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('dashboard_home'))

@app.route('/dashboard/home')
def dashboard_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    projects = Project.query.filter_by(user_id=user.id).count()
    
    return render_template('dashboard/home.html', user=user, announcements=announcements, projects_count=projects)

@app.route('/dashboard/projects', methods=['GET', 'POST'])
def dashboard_projects():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name')
            description = request.form.get('description')
            
            project = Project(
                name=name,
                description=description,
                user_id=user.id
            )
            db.session.add(project)
            db.session.commit()
            flash('项目创建成功', 'success')
        
        elif action == 'delete':
            project_id = request.form.get('project_id')
            project = Project.query.filter_by(id=project_id, user_id=user.id).first()
            
            if project:
                db.session.delete(project)
                db.session.commit()
                flash('项目已删除', 'success')
            else:
                flash('项目不存在或无权操作', 'error')
        
        elif action == 'update':
            project_id = request.form.get('project_id')
            project = Project.query.filter_by(id=project_id, user_id=user.id).first()
            
            if project:
                project.name = request.form.get('name')
                project.description = request.form.get('description')
                project.latest_version = request.form.get('latest_version')
                project.download_url = request.form.get('download_url')
                project.announcement = request.form.get('announcement')
                project.force_update = request.form.get('force_update') == 'on'
                db.session.commit()
                flash('项目更新成功', 'success')
            else:
                flash('项目不存在或无权操作', 'error')
        
        return redirect(url_for('dashboard_projects'))
    
    projects = Project.query.filter_by(user_id=user.id).order_by(Project.created_at.desc()).all()
    return render_template('dashboard/projects.html', user=user, projects=projects)

@app.route('/dashboard/my', methods=['GET', 'POST'])
def dashboard_my():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.nickname = request.form.get('nickname')
        
        # 处理头像上传
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename != '':
                # 在实际应用中，应该保存文件到存储服务并保存URL
                filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}.{avatar.filename.split('.')[-1]}"
                avatar.save(os.path.join('static', 'uploads', filename))
                user.avatar = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('个人信息已更新', 'success')
        return redirect(url_for('dashboard_my'))
    
    return render_template('dashboard/my.html', user=user)

# 辅助函数
def send_verification_email(user):
    token = user.dev_id
    verify_url = url_for('verify_email', token=token, _external=True)
    
    msg = Message(
        subject='请验证您的邮箱 - SimpleKeytime',
        recipients=[user.email],
        html=render_template('emails/verification.html', user=user, verify_url=verify_url)
    )
    
    try:
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"发送验证邮件失败: {e}")

@app.route('/test-email')
def test_email():
    msg = Message(
        subject='测试邮件',
        recipients=['wxcznb@qq.com'],
        body='这是一封测试邮件',
        html='<h1>这是一封HTML测试邮件</h1>'
    )
    try:
        mail.send(msg)
        return '邮件发送成功'
    except Exception as e:
        return f'邮件发送失败: {str(e)}'

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)
    app.run(debug=True)