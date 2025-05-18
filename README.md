# SimpleKeytime - 软件授权管理系统

<div align="center">
             <img src="https://img.wjwj.top/2025/05/11/56d49f560848d1f28e6356b77b50a8dd.png" alt="SKT Logo" width="256" />
             <h1>SimpleKeytime</h1>
</div>
<br>

**SimpleKeytime** 是一个专为开发者设计的现代化软件授权管理系统，提供完整的授权密钥管理、用户验证和软件更新解决方案。

-----------

服务支持：[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SimpleHac/SimpleKeytime) ![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white) ![Microsoft SQL](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?logo=microsoft-sql-server&logoColor=white)

使用技术：![Python](https://img.shields.io/badge/Python-14354C.svg?logo=python&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26.svg?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6.svg?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-323330.svg?logo=javascript&logoColor=F7DF1E) ![VueJS](https://img.shields.io/badge/Vue.js-35495e.svg?logo=vue.js&logoColor=4FC08D) ![tailwindcss](https://img.shields.io/badge/tailwindcss-38B2AC.svg?logo=tailwind-css&logoColor=white) ![sqlite](https://img.shields.io/badge/sqlite-07405e.svg?logo=sqlite&logoColor=white) 	![mysql](https://img.shields.io/badge/mysql-00000f.svg?logo=mysql&logoColor=white)

-----------
## ✨ 核心特性

- 🔑 **授权密钥管理** - 生成、分发和验证软件授权密钥
- 🔄 **自动更新系统** - 支持强制更新和可选更新
- 📊 **用户管理** - 管理软件用户和授权状态
- 📦 **项目管理** - 为每个软件项目单独管理版本和更新
- 🛡️ **安全验证** - 基于 Flask-Login 的安全认证系统
- 📱 **响应式设计** - 适配桌面和移动设备

## 🚀 快速开始

### 前置要求

- Python 3.8+
- SQLite/MySQL
- pip

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/simplekeytime.git
cd simplekeytime

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
vim config.py
# 编辑.env文件配置您的设置
```
### 运行SimpleKeytime
```bash
python3 app.py

### 初始化数据库（可选）

```bash
# 创建数据库表
flask db upgrade

# 创建默认管理员账户
flask create-admin
```

### 运行开发服务器（可选）

```bash
flask run
```

访问 [http://localhost:5000](http://localhost:5000) 开始使用（可自行修改地址）

## 🖥️ 系统架构

```
simplekeytime/
├── app.py                # 主应用入口
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
├── static/               # 静态资源
│   ├── css/              # 样式表
│   └── images/           # 图片资源
└── templates/            # 模板文件
    ├── auth/             # 认证相关模板
    ├── dashboard/        # 控制台模板
    └── emails/           # 邮件模板
```

## 🔒 默认管理员账户

- 用户名: `admin`
- 密码: `admin123`

**首次登录后请立即修改密码！**

## 🌐 生产环境部署

推荐使用以下方式部署生产环境：

1. **WSGI服务器**:
   - Gunicorn + Nginx
   - Waitress

2. **数据库**:
   - MySQL
   - PostgreSQL

3. **安全配置**:
   - 启用HTTPS
   - 设置强SECRET_KEY
   - 限制管理后台访问

## API开发文档
- DeepWiki AI文档：[DeepWiki/SimpleKeytime](https://deepwiki.com/SimpleHac/SimpleKeytime)
- SimpleHac官方文档：[https://skt.simplehac.cn/v1/api/doc](https://skt.simplehac.cn/v1/api/doc)

## 📄 开源协议

本项目采用 [MIT License](LICENSE)

## 🤝 参与贡献

欢迎提交Pull Request或Issue报告问题

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📧 联系我们

如有任何问题，请联系: [wxcznb@qq.com](mailto:wxcznb@qq.com)

---

**SimpleKeytime** © 2025 - 为开发者打造的优雅授权解决方案
