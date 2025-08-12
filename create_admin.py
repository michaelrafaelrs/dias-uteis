#!/usr/bin/env python3
import os
import sys

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.admin import Admin
from src.models.user import db
from src.main import app

def create_admin():
    with app.app_context():
        # Verifica se já existe um admin
        existing_admin = Admin.query.filter_by(username='admin').first()
        if not existing_admin:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Administrador criado com sucesso!')
            print('Usuário: admin')
            print('Senha: admin123')
        else:
            print('Administrador já existe')

if __name__ == '__main__':
    create_admin()
