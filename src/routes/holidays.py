from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.holiday import Holiday, db
from src.utils.business_days import fetch_national_holidays_from_api

holidays_bp = Blueprint('holidays', __name__)

@holidays_bp.route('/holidays', methods=['GET'])
def get_holidays():
    """Lista feriados com filtros opcionais"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    state = request.args.get('state')
    city = request.args.get('city')
    holiday_type = request.args.get('type')
    
    query = Holiday.query.filter(Holiday.is_active == True)
    
    if start_date:
        query = query.filter(Holiday.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Holiday.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if state:
        query = query.filter((Holiday.state == state) | (Holiday.type == 'nacional'))
    if city:
        query = query.filter((Holiday.city == city) | (Holiday.state == state) | (Holiday.type == 'nacional'))
    if holiday_type:
        query = query.filter(Holiday.type == holiday_type)
    
    holidays = query.order_by(Holiday.date).all()
    return jsonify([holiday.to_dict() for holiday in holidays])

@holidays_bp.route('/holidays', methods=['POST'])
def create_holiday():
    """Cria um novo feriado (apenas para admins)"""
    data = request.get_json()
    
    try:
        holiday = Holiday(
            name=data['name'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            type=data['type'],
            state=data.get('state'),
            city=data.get('city')
        )
        
        db.session.add(holiday)
        db.session.commit()
        
        return jsonify(holiday.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@holidays_bp.route('/holidays/<int:holiday_id>', methods=['PUT'])
def update_holiday(holiday_id):
    """Atualiza um feriado (apenas para admins)"""
    holiday = Holiday.query.get_or_404(holiday_id)
    data = request.get_json()
    
    try:
        holiday.name = data.get('name', holiday.name)
        if 'date' in data:
            holiday.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        holiday.type = data.get('type', holiday.type)
        holiday.state = data.get('state', holiday.state)
        holiday.city = data.get('city', holiday.city)
        holiday.is_active = data.get('is_active', holiday.is_active)
        
        db.session.commit()
        return jsonify(holiday.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@holidays_bp.route('/holidays/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    """Remove um feriado (apenas para admins)"""
    holiday = Holiday.query.get_or_404(holiday_id)
    holiday.is_active = False
    db.session.commit()
    return jsonify({'message': 'Feriado removido com sucesso'})

@holidays_bp.route('/holidays/import-national/<int:year>', methods=['POST'])
def import_national_holidays(year):
    """Importa feriados nacionais da Brasil API (apenas para admins)"""
    try:
        api_holidays = fetch_national_holidays_from_api(year)
        imported_count = 0
        
        for api_holiday in api_holidays:
            # Verifica se o feriado já existe
            existing = Holiday.query.filter_by(
                date=datetime.strptime(api_holiday['date'], '%Y-%m-%d').date(),
                type='nacional'
            ).first()
            
            if not existing:
                holiday = Holiday(
                    name=api_holiday['name'],
                    date=datetime.strptime(api_holiday['date'], '%Y-%m-%d').date(),
                    type='nacional'
                )
                db.session.add(holiday)
                imported_count += 1
        
        db.session.commit()
        return jsonify({
            'message': f'{imported_count} feriados nacionais importados para {year}',
            'imported_count': imported_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400