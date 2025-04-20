from app.extensions import db
from datetime import datetime
import json

class Setting(db.Model):
    """Model for storing system settings"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(16), nullable=False)  # string, integer, boolean, json
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, key, value, description=None):
        self.key = key
        self.value = value
        self.description = description

    @staticmethod
    def get_value(key, default=None):
        """Get a setting value by key"""
        setting = Setting.query.filter_by(key=key).first()
        if not setting:
            return default
        
        if setting.value_type == 'boolean':
            return setting.value.lower() == 'true'
        elif setting.value_type == 'integer':
            return int(setting.value)
        elif setting.value_type == 'json':
            return json.loads(setting.value)
        return setting.value

    @staticmethod
    def set_value(key, value, description=None):
        """Set a setting value by key"""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = Setting(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit() 