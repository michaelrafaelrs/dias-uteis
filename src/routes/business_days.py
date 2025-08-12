from flask import Blueprint, request, jsonify
from datetime import datetime
from src.utils.business_days import count_business_days, add_business_days, subtract_business_days

business_days_bp = Blueprint('business_days', __name__)

@business_days_bp.route('/business-days/count', methods=['POST'])
def count_days():
    """Conta dias úteis entre duas datas"""
    data = request.get_json()
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        state = data.get('state')
        city = data.get('city')
        
        business_days = count_business_days(start_date, end_date, state, city)
        
        return jsonify({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'business_days': business_days,
            'state': state,
            'city': city
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@business_days_bp.route('/business-days/add', methods=['POST'])
def add_days():
    """Adiciona dias úteis a uma data"""
    data = request.get_json()
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        days_to_add = int(data['days_to_add'])
        state = data.get('state')
        city = data.get('city')
        
        result_date = add_business_days(start_date, days_to_add, state, city)
        
        return jsonify({
            'start_date': start_date.isoformat(),
            'days_added': days_to_add,
            'result_date': result_date.isoformat(),
            'state': state,
            'city': city
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@business_days_bp.route('/business-days/subtract', methods=['POST'])
def subtract_days():
    """Subtrai dias úteis de uma data"""
    data = request.get_json()
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        days_to_subtract = int(data['days_to_subtract'])
        state = data.get('state')
        city = data.get('city')
        
        result_date = subtract_business_days(start_date, days_to_subtract, state, city)
        
        return jsonify({
            'start_date': start_date.isoformat(),
            'days_subtracted': days_to_subtract,
            'result_date': result_date.isoformat(),
            'state': state,
            'city': city
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
