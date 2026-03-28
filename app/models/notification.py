"""Modèle Notification — Table notifications."""
import uuid
from datetime import datetime
from app import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)  # transaction/securite/systeme/promotion
    canal = db.Column(db.String(20), default='web')  # web/email/sms
    titre = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    lu = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'canal': self.canal,
            'titre': self.titre,
            'message': self.message,
            'lu': self.lu,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
