from app import create_app, db
import click
from flask import current_app

app = create_app()

# 初始化数据库
@app.cli.command()
def initdb():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print('数据库初始化成功')
        
        # 创建默认管理员
        default_admin = current_app.config['ADMIN_EMAIL']
        admin = current_app.config['ADMIN_PASSWORD']
        
        # 检查默认管理员是否已存在
        with app.app_context():
            from app.models import User
            existing_admin = User.query.filter_by(email=default_admin).first()
            if not existing_admin:
                new_admin = User(
                    username='管理员',
                    email=default_admin
                )
                new_admin.set_password(admin)
                new_admin.is_active = True
                new_admin.is_admin = True
                
                db.session.add(new_admin)
                db.session.commit()
                print('默认管理员已创建')
            else:
                print('默认管理员已存在')

# 运行服务器
@click.command()
@click.option('--host', default='0.0.0.0', help='服务器地址')
@click.option('--port', default=80, help='服务器端口', type=int)
def run(host, port):
    """运行 SimpleKeytime 服务"""
    # 检查端口是否被占用
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error:
        print(f'错误：端口 {port} 已被占用，请选择其他端口')
        return
    finally:
        s.close()
    
    # 设置应用上下文
    with app.app_context():
        # 打印服务器信息
        protocol = 'HTTP' if port == 80 else 'HTTPS'
        print(f"\nSimpleKeytime 服务已启动")
        print(f"地址: {protocol}://{host}:{port}")
        
        # 获取 API 地址
        api_base_url = current_app.config['API_BASE_URL']
        print(f"API 地址: {protocol}://{host}:{port}{api_base_url}")
        
        # 获取管理员信息
        admin_email = current_app.config['ADMIN_EMAIL']
        print(f"管理员邮箱: {admin_email}")
        
        # 获取默认管理员密码 (注意：在生产环境中不应明文显示密码)
        # 仅用于演示和本地开发
        admin_password = current_app.config['ADMIN_PASSWORD']
        print(f"默认管理员密码: {admin_password}")
        print("\n注意：请立即修改默认管理员密码以确保安全\n")
        
        # 启动应用
        app.run(host=host, port=port)

if __name__ == '__main__':
    run()