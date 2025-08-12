from src.models.user import db
from datetime import date

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # nacional, estadual, municipal
    state = db.Column(db.String(2), nullable=True)  # sigla do estado (ex: SP, RJ)
    city = db.Column(db.String(100), nullable=True)  # nome da cidade
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Holiday {self.name} - {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat(),
            'type': self.type,
            'state': self.state,
            'city': self.city,
            'is_active': self.is_active
        }
