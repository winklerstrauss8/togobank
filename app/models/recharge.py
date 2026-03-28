"""Modèle Recharge Mobile — Table recharges_mobile."""
import uuid
from datetime import datetime
from app import db


class RechargeMobile(db.Model):
    __tablename__ = 'recharges_mobile'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    compte_id = db.Column(db.String(36), db.ForeignKey('comptes.id'), nullable=False)
    operateur = db.Column(db.String(20), nullable=False)  # mixx/flooz
    numero_tel = db.Column(db.String(20), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    frais = db.Column(db.Float, default=0.0)
    reference_interne = db.Column(db.String(30), unique=True, nullable=False)
    reference_externe = db.Column(db.String(100), nullable=True)
    statut = db.Column(db.String(20), default='en_cours')  # en_cours/valide/echoue/annule
    callback_data = db.Column(db.Text, nullable=True)  # JSON callback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'compte_id': self.compte_id,
            'operateur': self.operateur,
            'numero_tel': self.numero_tel,
            'montant': self.montant,
            'frais': self.frais,
            'reference_interne': self.reference_interne,
            'reference_externe': self.reference_externe,
            'statut': self.statut,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
