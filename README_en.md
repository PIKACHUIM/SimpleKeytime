<div align="center">
             <img src="https://img.wjwj.top/2025/05/11/56d49f560848d1f28e6356b77b50a8dd.png" alt="SKT Logo" width="256" />
             <h1>SimpleKeytime</h1>
             <a href="README.md">简体中文 README</a>
</div>
<br>

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-2.3.3-blue.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy Version](https://img.shields.io/badge/SQLAlchemy-2.0.23-blue.svg)](https://www.sqlalchemy.org/)

SimpleKeytime is an open-source software update, licensing, key management, and announcement notification system designed to provide developers with a simple and efficient management experience.

## 🌟 Key Features

- **🚀 User Management**: Supports user registration, login, and management for full control over user access.
- **⚙️ Application Management**: Create, edit, and delete applications to manage your software products with ease.
- **📝 Version Management**: Manage different versions of your applications, including release notes and download links, ensuring users always have access to the latest updates.
- **🔒 Licensing Management**: Supports version-based licensing and enforced updates to protect your intellectual property.
- **📢 Announcement Notifications**: Publish in-site announcements to keep users informed of important information.
- **🌐 API Integration**: Offers a comprehensive set of APIs for seamless integration with other systems, unlocking endless possibilities.

## 📦 Technology Stack

- **Python**: 3.11+
- **Flask**: 2.3.3
- **SQLAlchemy**: 2.0.23
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.0, JavaScript

## 🚀 Getting Started

### Environment Setup

1. **Install Python**: Ensure Python 3.11 or a newer version is installed.
2. **Install Dependencies**: Run the following command to install project dependencies.

```bash
pip install -r requirements.txt
```

### Initialize the Database

```bash
flask initdb
```

### Start the Server

```bash
python server.py
```

By default, the server will run on `http://127.0.0.1:80`. You can access the SimpleKeytime system at this address.

### Default Admin Account

- **Email**: admin@simplekeytime.com
- **Password**: admin (Please change the default password upon first login)

## 🛠️ Configuration

You can configure the project by creating a `.env` file or by directly modifying `config.py`. Here are some key configuration items:

```python
# Configuration file example
SECRET_KEY = 'your-secret-key-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SITE_NAME = 'SimpleKeytime'
SITE_DESC = 'Software Update and Licensing Management System'
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

## 📁 Project Structure

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

## 🤝 Contributing

Contributions are welcome! Please read the [Contribution Guidelines](CONTRIBUTING.md) to learn how to get involved.

## 👏 Acknowledgments

Thank you to all the developers and the open-source community for their contributions to this project.

## 📄 License

This project is open-sourced under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
