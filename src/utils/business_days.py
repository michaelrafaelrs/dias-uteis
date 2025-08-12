from datetime import date, timedelta
from src.models.holiday import Holiday
import requests

def is_weekend(date_obj):
    """Verifica se a data é fim de semana (sábado ou domingo)"""
    return date_obj.weekday() >= 5

def get_holidays_in_range(start_date, end_date, state=None, city=None):
    """Busca feriados no banco de dados dentro do período especificado"""
    query = Holiday.query.filter(
        Holiday.date >= start_date,
        Holiday.date <= end_date,
        Holiday.is_active == True
    )
    
    if state:
        query = query.filter((Holiday.state == state) | (Holiday.type == 'nacional'))
    if city:
        query = query.filter((Holiday.city == city) | (Holiday.state == state) | (Holiday.type == 'nacional'))
    
    return query.all()

def count_business_days(start_date, end_date, state=None, city=None):
    """Conta os dias úteis entre duas datas, excluindo fins de semana e feriados"""
    if start_date > end_date:
        return 0
    
    # Busca feriados no período
    holidays = get_holidays_in_range(start_date, end_date, state, city)
    holiday_dates = {holiday.date for holiday in holidays}
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        if not is_weekend(current_date) and current_date not in holiday_dates:
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

def add_business_days(start_date, business_days_to_add, state=None, city=None):
    """Adiciona dias úteis a uma data"""
    current_date = start_date
    days_added = 0
    
    while days_added < business_days_to_add:
        current_date += timedelta(days=1)
        
        # Busca feriados para a data atual
        holidays = get_holidays_in_range(current_date, current_date, state, city)
        holiday_dates = {holiday.date for holiday in holidays}
        
        if not is_weekend(current_date) and current_date not in holiday_dates:
            days_added += 1
    
    return current_date

def subtract_business_days(start_date, business_days_to_subtract, state=None, city=None):
    """Subtrai dias úteis de uma data"""
    current_date = start_date
    days_subtracted = 0
    
    while days_subtracted < business_days_to_subtract:
        current_date -= timedelta(days=1)
        
        # Busca feriados para a data atual
        holidays = get_holidays_in_range(current_date, current_date, state, city)
        holiday_dates = {holiday.date for holiday in holidays}
        
        if not is_weekend(current_date) and current_date not in holiday_dates:
            days_subtracted += 1
    
    return current_date

def fetch_national_holidays_from_api(year):
    """Busca feriados nacionais da Brasil API"""
    try:
        response = requests.get(f'https://brasilapi.com.br/api/feriados/v1/{year}')
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Erro ao buscar feriados da API: {e}")
        return []