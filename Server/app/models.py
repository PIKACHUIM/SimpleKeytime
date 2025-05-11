from datetime import datetime

from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import Serializer, TimestampSigner
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    avatar = db.Column(db.String(200), default='default-avatar.jpg')
    developer_id = db.Column(db.String(36), unique=True, nullable=False)
    
    apps = db.relationship('Application', backref='developer', lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 生成唯一的开发者ID
        self.developer_id = str(uuid.uuid4())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_activation_token(self, expires_in=3600):
        signer = TimestampSigner(current_app.config['SECRET_KEY'])
        serializer = Serializer(current_app.config['SECRET_KEY'])
        payload = {'user_id': self.id}
        payload['timestamp'] = signer.sign(serializer.dumps(payload)).decode('utf-8')
        return serializer.dumps(payload).decode('utf-8')

    @staticmethod
    def verify_activation_token(token, max_age=3600):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        signer = TimestampSigner(current_app.config['SECRET_KEY'])
    
        try:
            payload = serializer.loads(token, max_age=max_age)
            # 验证时间戳
            signer.unsign(payload.pop('timestamp'))
            return User.query.get(payload.get('user_id'))
        except:
            return None
    
    def __repr__(self):
        return f'<User {self.username}>'

class Application(db.Model):
    app_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    latest_version = db.Column(db.String(20), nullable=False, default='1.0.0')
    download_url = db.Column(db.String(200), nullable=True)
    update_log = db.Column(db.Text, nullable=True)
    force_update = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Application {self.name}>'

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_top = db.Column(db.Boolean, default=False)
    is_read = db.relationship('UserAnnouncement', backref='announcement', lazy=True)
    
    def __repr__(self):
        return f'<Announcement {self.title}>'

class UserAnnouncement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcement.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserAnnouncement {self.user_id} - {self.announcement_id}>'