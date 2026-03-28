#Modèle Compte Bancaire — Table comptes.
import uuid
import random
from datetime import datetime, date
from app import db


class Compte(db.Model):
    __tablename__ = 'comptes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_compte = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type_compte = db.Column(db.String(20), nullable=False)  # courant/epargne/pro/jeune
    libelle = db.Column(db.String(100), nullable=True)
    solde = db.Column(db.Float, nullable=False, default=0.0)
    solde_bloque = db.Column(db.Float, default=0.0)
    devise = db.Column(db.String(3), default='XOF')
    statut = db.Column(db.String(20), default='actif')  # actif/suspendu/cloture
    decouvert_autorise = db.Column(db.Float, default=0.0)
    plafond_journalier = db.Column(db.Float, default=500000.0)
    plafond_mensuel = db.Column(db.Float, default=5000000.0)
    date_ouverture = db.Column(db.Date, nullable=False, default=date.today)
    date_cloture = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    transactions_source = db.relationship('Transaction', backref='compte_source_rel',
                                          foreign_keys='Transaction.compte_source_id', lazy='dynamic')
    transactions_dest = db.relationship('Transaction', backref='compte_dest_rel',
                                        foreign_keys='Transaction.compte_dest_id', lazy='dynamic')
    cartes = db.relationship('CarteBancaire', backref='compte', lazy='dynamic')
    recharges = db.relationship('RechargeMobile', backref='compte', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'numero_compte': self.numero_compte,
            'user_id': self.user_id,
            'type_compte': self.type_compte,
            'libelle': self.libelle or self._default_libelle(),
            'solde': self.solde,
            'solde_bloque': self.solde_bloque,
            'solde_disponible': self.solde - self.solde_bloque,
            'devise': self.devise,
            'statut': self.statut,
            'plafond_journalier': self.plafond_journalier,
            'plafond_mensuel': self.plafond_mensuel,
            'date_ouverture': self.date_ouverture.isoformat() if self.date_ouverture else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def _default_libelle(self):
        labels = {
            'courant': 'Compte Courant',
            'epargne': 'Compte Épargne',
            'pro': 'Compte Professionnel',
            'jeune': 'Compte Jeune'
        }
        return labels.get(self.type_compte, 'Compte')

    @staticmethod
    def generate_numero_compte():
        """Génère un numéro de compte TG + 18 chiffres."""
        return f"TG{''.join([str(random.randint(0,9)) for _ in range(18)])}"
