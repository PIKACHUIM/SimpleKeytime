# SimpleKeytime - 软件授权管理系统

<div align="center">
             <img src="https://img.wjwj.top/2025/05/11/56d49f560848d1f28e6356b77b50a8dd.png" alt="SKT Logo" width="256" />
             <h1>SimpleKeytime</h1>
</div>
<br>

**SimpleKeytime** 是一个专为开发者设计的现代化软件授权管理系统，提供完整的授权密钥管理、用户验证和软件更新解决方案。

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
cp .env.example .env
# 编辑.env文件配置您的设置
```

### 初始化数据库

```bash
# 创建数据库表
flask db upgrade

# 创建默认管理员账户
flask create-admin
```

### 运行开发服务器

```bash
flask run
```

访问 [http://localhost:5000](http://localhost:5000) 开始使用

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

如有任何问题，请联系: [your.email@example.com](mailto:your.email@example.com)

---

**SimpleKeytime** © 2025 - 为开发者打造的优雅授权解决方案