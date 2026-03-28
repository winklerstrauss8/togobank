"""Modèle Utilisateur — Table users."""
import uuid
from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_client = db.Column(db.String(12), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # client/agent/admin/super_admin
    statut = db.Column(db.String(20), nullable=False, default='actif')  # actif/suspendu/bloque/en_attente
    type_client = db.Column(db.String(20), nullable=False, default='particulier')  # particulier/entreprise

    date_naissance = db.Column(db.Date, nullable=True)
    adresse = db.Column(db.Text, nullable=True)
    ville = db.Column(db.String(100), nullable=True)
    photo_profil = db.Column(db.String(255), nullable=True)
    piece_identite = db.Column(db.String(255), nullable=True)

    kyc_valide = db.Column(db.Boolean, default=False)
    kyc_valide_par = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    kyc_valide_le = db.Column(db.DateTime, nullable=True)

    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_secret = db.Column(db.String(64), nullable=True)

    derniere_connexion = db.Column(db.DateTime, nullable=True)
    tentatives_connexion = db.Column(db.Integer, default=0)
    bloque_jusqu_au = db.Column(db.DateTime, nullable=True)

    notification_email = db.Column(db.Boolean, default=True)
    notification_sms = db.Column(db.Boolean, default=True)
    langue = db.Column(db.String(5), default='fr')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    comptes = db.relationship('Compte', backref='proprietaire', lazy='dynamic', foreign_keys='Compte.user_id')
    notifications = db.relationship('Notification', backref='utilisateur', lazy='dynamic')
    beneficiaires = db.relationship('Beneficiaire', backref='utilisateur', lazy='dynamic')

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'numero_client': self.numero_client,
            'nom': self.nom,
            'prenom': self.prenom,
            'nom_complet': f"{self.prenom} {self.nom}",
            'email': self.email,
            'telephone': self.telephone,
            'role': self.role,
            'statut': self.statut,
            'type_client': self.type_client,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'ville': self.ville,
            'photo_profil': self.photo_profil,
            'kyc_valide': self.kyc_valide,
            'two_fa_enabled': self.two_fa_enabled,
            'langue': self.langue,
            'derniere_connexion': self.derniere_connexion.isoformat() if self.derniere_connexion else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        return data

    @staticmethod
    def generate_numero_client():
        """Génère un numéro client unique TGB-XXXXXXXX."""
        import random
        return f"TGB{random.randint(10000000, 99999999)}"
