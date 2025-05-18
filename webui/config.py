import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 邮件配置
    MAIL_SERVER = ''  # SMTP服务器地址
    MAIL_PORT = 465  # 端口
    MAIL_USE_SSL = True # SSL
    MAIL_USE_TLS = False  # TLS
    MAIL_USERNAME = '' # 邮件用户名
    MAIL_PASSWORD = '' # 密码
    MAIL_DEFAULT_SENDER = '' # 发件人，通常等于用户名
    
    # 禁用SSL证书验证
    MAIL_SUPPRESS_SEND = False  # 确保邮件发送不被抑制
    MAIL_DEBUG = True  # 调试模式可以看到更多信息
    
    # 应用配置
    APP_NAME = 'SimpleKeytime' # 网站名
    APP_DESCRIPTION = '简单易用的软件授权管理系统' # 描述
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000') # 变量调用的站点地址
    APP_PORT = 5000
