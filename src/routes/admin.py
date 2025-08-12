from flask import Blueprint, request, jsonify, session
from src.models.admin import Admin, db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['POST'])
def login():
    """Login de administrador"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    admin = Admin.query.filter_by(username=username, is_active=True).first()
    
    if admin and admin.check_password(password):
        session['admin_id'] = admin.id
        session['is_admin'] = True
        return jsonify({
            'message': 'Login realizado com sucesso',
            'admin': admin.to_dict()
        })
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401

@admin_bp.route('/admin/logout', methods=['POST'])
def logout():
    """Logout de administrador"""
    session.pop('admin_id', None)
    session.pop('is_admin', None)
    return jsonify({'message': 'Logout realizado com sucesso'})

@admin_bp.route('/admin/check', methods=['GET'])
def check_admin():
    """Verifica se o usuário está logado como admin"""
    if session.get('is_admin'):
        admin = Admin.query.get(session.get('admin_id'))
        if admin and admin.is_active:
            return jsonify({
                'is_admin': True,
                'admin': admin.to_dict()
            })
    
    return jsonify({'is_admin': False})

@admin_bp.route('/admin/create', methods=['POST'])
def create_admin():
    """Cria um novo administrador (apenas para desenvolvimento)"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    # Verifica se já existe um admin com esse username
    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        return jsonify({'error': 'Username já existe'}), 400
    
    admin = Admin(username=username)
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    return jsonify({
        'message': 'Administrador criado com sucesso',
        'admin': admin.to_dict()
    }), 201
