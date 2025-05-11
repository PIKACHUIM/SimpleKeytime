<div align="center">
             <img src="https://img.wjwj.top/2025/05/11/56d49f560848d1f28e6356b77b50a8dd.png" alt="SKT Logo" width="256" />
             <h1>SimpleKeytime</h1>
             <a href="README_en.md">English README</a>
</div>
<br>

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-2.3.3-blue.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy Version](https://img.shields.io/badge/SQLAlchemy-2.0.23-blue.svg)](https://www.sqlalchemy.org/)


SimpleKeytime 是一个开源的软件更新、授权、卡密管理及公告通知系统，旨在为开发者提供简洁高效的管理体验。

## 🌟 主要特点

- **🚀 用户管理**：支持用户注册、登录和管理，轻松掌控用户权限。
- **⚙️ 应用管理**：创建、编辑和删除应用，灵活管理您的软件产品。
- **📝 版本管理**：管理应用的不同版本，包括更新日志和下载地址，确保用户始终使用最新版本。
- **🔒 授权管理**：支持按版本授权和强制更新，保护您的知识产权。
- **📢 公告通知**：发布站内公告，及时通知用户重要信息，保持沟通畅通。
- **🌐 API 接口**：提供丰富的 API 接口，方便与其他系统集成，拓展无限可能。

## 📦 技术栈

- **Python**：3.11+
- **Flask**：2.3.3
- **SQLAlchemy**：2.0.23
- **前端**：HTML5, CSS3, Bootstrap 5.3.0, JavaScript

## 🚀 快速开始

### 环境准备

1. **安装 Python**：确保已安装 Python 3.11 或更高版本。
2. **安装依赖**：运行以下命令安装项目依赖。

```bash
pip install -r requirements.txt
```

### 初始化数据库

```bash
flask initdb
```

### 启动服务

```bash
python server.py
```

默认情况下，服务将运行在 `http://127.0.0.1:80`，您可以访问该地址以查看 SimpleKeytime 系统。

### 默认管理员账户

- **邮箱**：admin@simplekeytime.com
- **密码**：admin（请尽快修改默认密码）

## 🛠️ 配置

您可以通过创建 `.env` 文件或直接修改 `config.py` 来配置项目。以下是一些关键配置项：

```python
# 配置文件示例
SECRET_KEY = 'your-secret-key-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SITE_NAME = 'SimpleKeytime'
SITE_DESC = '软件更新与授权管理系统'
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'admin'
API_BASE_URL = '/api'
SITE_URL = 'http://127.0.0.1'
MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_USERNAME = 'your-email@example.com'
MAIL_PASSWORD = 'your-email-password'
MAIL_DEFAULT_SENDER = 'noreply@example.com'
```

## 📁 项目结构

```
simplekeytime/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── admin.py
│   │   └── api.py
│   ├── templates/
│   │   ├── index.html
│   │   └── webui/
│   │       ├── dashboard.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── profile.html
│   │       ├── projects.html
│   │       ├── announcements.html
│   │       └── email/
│   │           └── activation.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── config.py
├── server.py
└── requirements.txt
```

## 🤝 贡献

欢迎贡献代码！请阅读 [贡献指南](CONTRIBUTING.md) 了解如何参与项目。

## 👏 致谢

感谢所有为该项目做出贡献的开发者和开源社区的支持。

## 📄 开源协议

本项目采用 MIT 协议开源。详情请参阅 [LICENSE](LICENSE) 文件。