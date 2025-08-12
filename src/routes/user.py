# src/routes/user.py
from flask import Blueprint, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def list_users():
    return jsonify({"message": "Listagem de usuários"})
