from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import Announcement, Application, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

api_bp = Blueprint('api', __name__)

# API健康检查
@api_bp.route('/status')
def status():
    return jsonify({
        'status': 'ok',
        'message': 'SimpleKeytime API 正在运行'
    })

# 用户认证
@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    developer_id = data.get('developer_id')
    app_id = data.get('app_id')
    
    if not developer_id or not app_id:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 检查用户是否存在
    user = User.query.filter_by(developer_id=developer_id).first()
    if not user:
        return jsonify({'error': '无效的开发者ID'}), 401
    
    # 检查应用是否存在
    app = Application.query.filter_by(app_id=app_id, user_id=user.id).first()
    if not app:
        return jsonify({'error': '无效的应用ID'}), 401
    
    # 生成访问令牌
    access_token = create_access_token(identity={
        'user_id': user.id,
        'developer_id': user.developer_id,
        'app_id': app.app_id,
        'is_admin': user.is_admin
    })
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': 3600
    })

# 检查更新
@api_bp.route('/check-update', methods=['POST'])
@jwt_required()
def check_update():
    data = request.json
    current_version = data.get('current_version')
    
    if not current_version:
        return jsonify({'error': '缺少版本信息'}), 400
    
    # 获取认证信息
    identity = get_jwt_identity()
    app = Application.query.get(identity.get('app_id'))
    
    # 比较版本
    if not app:
        return jsonify({'error': '应用不存在'}), 404
    
    # 简单的版本比较
    def version_tuple(v):
        return tuple(map(int, (v.split("-")[0]).split('.')))
    
    is_update_available = False
    latest_version = app.latest_version
    
    if version_tuple(current_version) < version_tuple(latest_version):
        is_update_available = True
    
    return jsonify({
        'update_available': is_update_available,
        'latest_version': latest_version,
        'download_url': app.download_url,
        'update_log': app.update_log,
        'force_update': app.force_update,
        'is_public': app.is_public
    })

# 获取公告
@api_bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    # 获取认证信息
    identity = get_jwt_identity()
    
    # 查询公告
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    
    # 格式化公告
    result = []
    for announcement in announcements:
        result.append({
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'created_at': announcement.created_at.isoformat(),
            'is_top': announcement.is_top
        })
    
    return jsonify(result)

# 获取应用信息
@api_bp.route('/app/<int:app_id>', methods=['GET'])
@jwt_required()
def get_app_info(app_id):
    # 获取认证信息
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    
    # 检查权限
    if user_id != identity.get('app_id'):
        return jsonify({'error': '权限不足'}), 403
    
    app = Application.query.get(app_id)
    if not app:
        return jsonify({'error': '应用不存在'}), 404
    
    return jsonify({
        'app_id': app.app_id,
        'name': app.name,
        'description': app.description,
        'latest_version': app.latest_version,
        'download_url': app.download_url,
        'update_log': app.update_log,
        'force_update': app.force_update,
        'is_public': app.is_public
    })

# 获取用户信息
@api_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_info():
    # 获取认证信息
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'developer_id': user.developer_id,
        'email': user.email,
        'avatar': user.avatar,
        'is_active': user.is_active,
        'is_admin': user.is_admin
    })