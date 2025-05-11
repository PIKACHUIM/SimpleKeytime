from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Application, Announcement, UserAnnouncement
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('dashboard.index'))

@admin_bp.route('/')
def index():
    user_count = User.query.count()
    active_user_count = User.query.filter_by(is_active=True).count()
    app_count = Application.query.count()
    announcement_count = Announcement.query.count()
    
    return render_template('webui/admin/index.html', 
                          user_count=user_count,
                          active_user_count=active_user_count,
                          app_count=app_count,
                          announcement_count=announcement_count)

@admin_bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    return render_template('webui/admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    apps = Application.query.filter_by(user_id=user_id)
    return render_template('webui/admin/user_detail.html', user=user, apps=apps)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.is_active = 'is_active' in request.form
        user.is_admin = 'is_admin' in request.form
        
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('webui/admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/change-password', methods=['POST'])
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    password = request.form.get('password')
    
    user.set_password(password)
    db.session.commit()
    
    flash('密码已更新', 'success')
    return redirect(url_for('admin.user_detail', user_id=user.id))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # 不能删除管理员自己
    if user.is_admin and current_user.id == user.id:
        flash('您不能删除自己的账户', 'warning')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('用户已删除', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/announcements')
def announcements():
    page = request.args.get('page', 1, type=int)
    announcements = Announcement.query.paginate(page=page, per_page=10)
    return render_template('webui/admin/announcements.html', announcements=announcements)

@admin_bp.route('/announcements/create', methods=['GET', 'POST'])
def create_announcement():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_top = 'is_top' in request.form
        
        announcement = Announcement(
            title=title,
            content=content,
            is_top=is_top
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        # 清除所有用户的公告阅读状态（可选）
        UserAnnouncement.query.filter(UserAnnouncement.announcement_id == announcement.id).delete()
        
        flash('公告已发布', 'success')
        return redirect(url_for('admin.announcements'))
    
    return render_template('webui/admin/create_announcement.html')

@admin_bp.route('/announcements/<int:announcement_id>/edit', methods=['GET', 'POST'])
def edit_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    if request.method == 'POST':
        announcement.title = request.form.get('title')
        announcement.content = request.form.get('content')
        announcement.is_top = 'is_top' in request.form
        
        db.session.commit()
        
        # 清除所有用户的公告阅读状态（可选）
        UserAnnouncement.query.filter(UserAnnouncement.announcement_id == announcement.id).delete()
        
        flash('公告已更新', 'success')
        return redirect(url_for('admin.announcements'))
    
    return render_template('webui/admin/edit_announcement.html', announcement=announcement)

@admin_bp.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    db.session.delete(announcement)
    db.session.commit()
    
    flash('公告已删除', 'success')
    return redirect(url_for('admin.announcements'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # 站点设置
        site_name = request.form.get('site_name')
        site_desc = request.form.get('site_desc')
        
        # 邮件设置
        mail_server = request.form.get('mail_server')
        mail_port = request.form.get('mail_port')
        mail_use_ssl = 'mail_use_ssl' in request.form
        mail_use_tls = 'mail_use_tls' in request.form
        mail_username = request.form.get('mail_username')
        mail_password = request.form.get('mail_password')
        mail_default_sender = request.form.get('mail_default_sender')
        
        # API设置
        api_base_url = request.form.get('api_base_url')
        
        # 更新配置
        current_app.config['SITE_NAME'] = site_name
        current_app.config['SITE_DESC'] = site_desc
        current_app.config['MAIL_SERVER'] = mail_server
        current_app.config['MAIL_PORT'] = int(mail_port)
        current_app.config['MAIL_USE_SSL'] = mail_use_ssl
        current_app.config['MAIL_USE_TLS'] = mail_use_tls
        current_app.config['MAIL_USERNAME'] = mail_username
        current_app.config['MAIL_PASSWORD'] = mail_password
        current_app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender
        current_app.config['API_BASE_URL'] = api_base_url
        
        flash('设置已保存', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('webui/admin/settings.html')