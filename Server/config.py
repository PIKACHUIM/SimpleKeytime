import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', True)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # 默认管理员账户
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    # 站点配置
    SITE_NAME = os.environ.get('SITE_NAME', 'SimpleKeytime')
    SITE_DESC = os.environ.get('SITE_DESC', '软件更新与授权管理系统')
    API_BASE_URL = os.environ.get('API_BASE_URL', '/api')
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost')
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-here')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)