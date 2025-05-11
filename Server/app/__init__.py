from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    
    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # 注册蓝本
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp, url_prefix='/webui/admin')
    app.register_blueprint(api_bp, url_prefix=app.config['API_BASE_URL'])
    
    # 创建所有数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员
        from app.models import User
        default_admin = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
        if not default_admin:
            admin = User(
                username='admin',
                email=app.config['ADMIN_EMAIL']
            )
            admin.set_password(app.config['ADMIN_PASSWORD'])
            admin.is_active = True
            admin.is_admin = True
            
            db.session.add(admin)
            db.session.commit()
    
    return app