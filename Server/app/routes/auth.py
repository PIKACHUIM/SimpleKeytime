from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from app import db, mail
from app.models import User
from flask_mail import Message
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证表单数据
        if not username or not email or not password or not confirm_password:
            flash('请填写所有必填字段', 'danger')
            return render_template('webui/register.html', 
                                  site_name=current_app.config['SITE_NAME'],
                                  api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                                  admin_email=current_app.config['ADMIN_EMAIL'])
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('webui/register.html', 
                                  site_name=current_app.config['SITE_NAME'],
                                  api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                                  admin_email=current_app.config['ADMIN_EMAIL'])
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('该邮箱已被注册', 'danger')
            return render_template('webui/register.html', 
                                  site_name=current_app.config['SITE_NAME'],
                                  api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                                  admin_email=current_app.config['ADMIN_EMAIL'])
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('该用户名已被使用', 'danger')
            return render_template('webui/register.html', 
                                  site_name=current_app.config['SITE_NAME'],
                                  api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                                  admin_email=current_app.config['ADMIN_EMAIL'])
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # 发送激活邮件
        from flask_mail import Message
        from app import mail
        
        activation_token = new_user.generate_activation_token()
        activation_url = url_for('auth.activate', token=activation_token, _external=True)
        
        msg = Message(
            subject='激活您的账户',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[new_user.email],
            html=render_template('email/activation.html', 
                                site_name=current_app.config['SITE_NAME'],
                                logo_url=url_for('static', filename='img/logo.svg', _external=True),
                                user=new_user,
                                activation_url=activation_url)
        )
        
        mail.send(msg)
        
        flash('注册成功！请检查您的邮箱以激活账户', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('webui/register.html', 
                           site_name=current_app.config['SITE_NAME'],
                           api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                           admin_email=current_app.config['ADMIN_EMAIL'])

@auth_bp.route('/activate/<token>')
def activate(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if user and not user.is_active:
            user.is_active = True
            db.session.commit()
            flash('账户已成功激活！', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('激活失败或账户已激活', 'danger')
            return redirect(url_for('auth.login'))
    except (SignatureExpired, BadTimeSignature):
        flash('激活链接已失效或无效', 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('邮箱或密码错误', 'danger')
            return render_template('webui/login.html', 
                                  site_name=current_app.config['SITE_NAME'],
                                  api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                                  admin_email=current_app.config['ADMIN_EMAIL'])
        
        if not user.is_active:
            flash('账户未激活，请检查邮箱并激活账户', 'warning')
            return render_template('webui/login.html', 
                                  site_name=current_app.config['SITE_NAME'],
                                  api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                                  admin_email=current_app.config['ADMIN_EMAIL'])
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        flash('登录成功!', 'success')
        return redirect(next_page)
    
    return render_template('webui/login.html', 
                           site_name=current_app.config['SITE_NAME'],
                           api_base_url=current_app.config['SITE_URL'] + current_app.config['API_BASE_URL'],
                           admin_email=current_app.config['ADMIN_EMAIL'])

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(email, salt='password-reset')
            
            msg = Message(
                subject='重置您的 SimpleKeytime 密码',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email],
                html=render_template('email/password_reset.html', 
                                   username=user.username, 
                                   url=url_for('auth.reset_password', token=token, _external=True))
            )
            
            try:
                mail.send(msg)
                flash('密码重置链接已发送到您的邮箱', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                current_app.logger.error(f'发送邮件失败: {str(e)}')
                flash('邮件发送失败，请重试', 'danger')
        else:
            flash('未找到该邮箱对应的用户', 'danger')
    
    return render_template('webui/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('无效的重置链接', 'danger')
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('两次输入的密码不一致', 'danger')
                return render_template('webui/reset_password.html')
            
            user.set_password(password)
            db.session.commit()
            flash('密码已成功重置！', 'success')
            return redirect(url_for('auth.login'))
        
        return render_template('webui/reset_password.html')
    
    except (SignatureExpired, BadTimeSignature):
        flash('重置链接已失效或无效', 'danger')
        return redirect(url_for('auth.forgot_password'))