# Modèle Carte Bancaire — Table cartes_bancaires.
import uuid
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from app import db


class CarteBancaire(db.Model):
    __tablename__ = 'cartes_bancaires'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    compte_id = db.Column(db.String(36), db.ForeignKey('comptes.id'), nullable=False)
    numero_masque = db.Column(db.String(19), nullable=False)  # **** **** **** 1234
    numero_complet = db.Column(db.String(19), nullable=False)
    type_carte = db.Column(db.String(20), nullable=False, default='virtuelle')  # virtuelle/physique
    date_expiration = db.Column(db.String(5), nullable=False)  # MM/YY
    cvv = db.Column(db.String(3), nullable=False)
    nom_porteur = db.Column(db.String(100), nullable=False)
    plafond = db.Column(db.Float, default=200000.0)
    statut = db.Column(db.String(20), default='active')  # active/bloquee/expiree
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, show_full=False):
        data = {
            'id': self.id,
            'compte_id': self.compte_id,
            'numero_masque': self.numero_masque,
            'type_carte': self.type_carte,
            'date_expiration': self.date_expiration,
            'nom_porteur': self.nom_porteur,
            'plafond': self.plafond,
            'statut': self.statut,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if show_full:
            data['numero_complet'] = self.numero_complet
            data['cvv'] = self.cvv
        return data

    @staticmethod
    def generate_card():
        """Génère les données d'une carte virtuelle."""
        num = '4' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        masque = f"**** **** **** {num[-4:]}"
        formatted = f"{num[:4]} {num[4:8]} {num[8:12]} {num[12:16]}"
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        now = datetime.utcnow()
        exp = f"{(now.month):02d}/{str(now.year + 3)[-2:]}"
        return formatted, masque, cvv, exp
