from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Application, Announcement, UserAnnouncement
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # 获取用户的应用
    apps = Application.query.filter_by(user_id=current_user.id)
    
    # 获取最近公告
    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    unread_announcements = []
    
    for announcement in recent_announcements:
        user_announcement = UserAnnouncement.query.filter_by(
            user_id=current_user.id,
            announcement_id=announcement.id
        ).first()
        
        if not user_announcement:
            unread_announcements.append(announcement)
    
    # 获取统计信息
    stats = {
        'app_count': apps.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'pending_updates': Application.query.filter_by(force_update=True).count(),
        'unread_announcements': len(unread_announcements)
    }
    
    return render_template('webui/dashboard.html', 
                          apps=apps, 
                          stats=stats, 
                          announcements=recent_announcements, 
                          unread_announcements=unread_announcements)

@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('webui/profile.html')

@dashboard_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == 'POST':
        username = request.form.get('username')
        avatar = request.form.get('avatar')
        
        current_user.username = username
        current_user.avatar = avatar
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('webui/profile_edit.html')

@dashboard_bp.route('/projects')
@login_required
def projects():
    apps = Application.query.filter_by(user_id=current_user.id).all()
    return render_template('webui/projects.html', apps=apps)

@dashboard_bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        latest_version = request.form.get('latest_version', '1.0.0')
        download_url = request.form.get('download_url')
        update_log = request.form.get('update_log')
        force_update = 'force_update' in request.form
        
        app = Application(
            name=name,
            description=description,
            user_id=current_user.id,
            latest_version=latest_version,
            download_url=download_url,
            update_log=update_log,
            force_update=force_update
        )
        
        db.session.add(app)
        db.session.commit()
        
        flash('应用创建成功', 'success')
        return redirect(url_for('dashboard.projects'))
    
    return render_template('webui/create_project.html')

@dashboard_bp.route('/projects/<int:app_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(app_id):
    app = Application.query.get_or_404(app_id)
    
    if app.user_id != current_user.id:
        flash('您没有权限编辑此应用', 'danger')
        return redirect(url_for('dashboard.projects'))
    
    if request.method == 'POST':
        app.name = request.form.get('name')
        app.description = request.form.get('description')
        app.latest_version = request.form.get('latest_version', '1.0.0')
        app.download_url = request.form.get('download_url')
        app.update_log = request.form.get('update_log')
        app.force_update = 'force_update' in request.form
        
        db.session.commit()
        
        flash('应用更新成功', 'success')
        return redirect(url_for('dashboard.projects'))
    
    return render_template('webui/edit_project.html', app=app)

@dashboard_bp.route('/projects/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_project(app_id):
    app = Application.query.get_or_404(app_id)
    
    if app.user_id != current_user.id:
        flash('您没有权限删除此应用', 'danger')
        return redirect(url_for('dashboard.projects'))
    
    db.session.delete(app)
    db.session.commit()
    
    flash('应用已删除', 'success')
    return redirect(url_for('dashboard.projects'))

@dashboard_bp.route('/announcements')
@login_required
def announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    
    # 标记已读公告
    for announcement in announcements:
        if not UserAnnouncement.query.filter_by(
            user_id=current_user.id,
            announcement_id=announcement.id
        ).first():
            user_announcement = UserAnnouncement(
                user_id=current_user.id,
                announcement_id=announcement.id
            )
            db.session.add(user_announcement)
    db.session.commit()
    
    return render_template('webui/announcements.html', announcements=announcements)

@dashboard_bp.route('/announcements/<int:announcement_id>')
@login_required
def announcement_detail(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    # 标记为已读
    if not UserAnnouncement.query.filter_by(
        user_id=current_user.id,
        announcement_id=announcement.id
    ).first():
        user_announcement = UserAnnouncement(
            user_id=current_user.id,
            announcement_id=announcement.id
        )
        db.session.add(user_announcement)
        db.session.commit()
    
    return render_template('webui/announcement_detail.html', announcement=announcement)