# Modèle Bénéficiaire — Table beneficiaires.
import uuid
from datetime import datetime
from app import db


class Beneficiaire(db.Model):
    __tablename__ = 'beneficiaires'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    numero_compte = db.Column(db.String(20), nullable=True)
    banque = db.Column(db.String(100), nullable=True, default='TogoBank')
    telephone = db.Column(db.String(20), nullable=True)
    categorie = db.Column(db.String(50), nullable=True)  # famille/amis/fournisseurs
    favori = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nom': self.nom,
            'numero_compte': self.numero_compte,
            'banque': self.banque,
            'telephone': self.telephone,
            'categorie': self.categorie,
            'favori': self.favori,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
