# Modèle AuditLog — Table audit_logs pour la conformité.
import uuid
from datetime import datetime
from app import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entite = db.Column(db.String(50), nullable=True)
    entite_id = db.Column(db.String(36), nullable=True)
    ancienne_valeur = db.Column(db.Text, nullable=True)
    nouvelle_valeur = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entite': self.entite,
            'entite_id': self.entite_id,
            'ip': self.ip,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
