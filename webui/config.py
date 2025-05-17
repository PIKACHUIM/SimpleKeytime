import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 邮件配置 - 不安全的SSL
    MAIL_SERVER = 'smtp.simplehac.cn'  # SMTP服务器地址
    MAIL_PORT = 465  # SSL端口
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False  # 确保TLS关闭
    MAIL_USERNAME = 'no-reply@simplehac.cn'
    MAIL_PASSWORD = 'ACBacb090723'
    MAIL_DEFAULT_SENDER = 'no-reply@simplehac.cn'
    
    # 禁用SSL证书验证
    MAIL_SUPPRESS_SEND = False  # 确保邮件发送不被抑制
    MAIL_DEBUG = True  # 调试模式可以看到更多信息
    
    # 应用配置
    APP_NAME = 'SimpleKeytime'
    APP_DESCRIPTION = '简单易用的软件授权管理系统'
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')