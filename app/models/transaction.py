"""Modèle Transaction — Table transactions."""
import uuid
from datetime import datetime, date
from app import db


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reference = db.Column(db.String(30), unique=True, nullable=False)
    compte_source_id = db.Column(db.String(36), db.ForeignKey('comptes.id'), nullable=True)
    compte_dest_id = db.Column(db.String(36), db.ForeignKey('comptes.id'), nullable=True)
    type_transaction = db.Column(db.String(20), nullable=False)
    # virement/recharge/retrait/frais/interet/remboursement
    montant = db.Column(db.Float, nullable=False)
    devise = db.Column(db.String(3), default='XOF')
    frais = db.Column(db.Float, default=0.0)
    taux_change = db.Column(db.Float, default=1.0)
    statut = db.Column(db.String(20), default='en_cours')
    # en_cours/valide/echoue/annule/rembourse
    canal = db.Column(db.String(20), nullable=False)
    # web/mobile/api/agence/mixx/flooz
    description = db.Column(db.Text, nullable=True)
    motif = db.Column(db.String(255), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)  # JSON stocké en texte
    ip_source = db.Column(db.String(45), nullable=True)
    valide_par = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    date_valeur = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'reference': self.reference,
            'compte_source_id': self.compte_source_id,
            'compte_dest_id': self.compte_dest_id,
            'type_transaction': self.type_transaction,
            'montant': self.montant,
            'devise': self.devise,
            'frais': self.frais,
            'statut': self.statut,
            'canal': self.canal,
            'description': self.description,
            'motif': self.motif,
            'date_valeur': self.date_valeur.isoformat() if self.date_valeur else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def generate_reference():
        """Génère une référence unique TXN-YYYYMMDD-XXXX."""
        import random
        d = datetime.utcnow().strftime('%Y%m%d')
        rand = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"TXN-{d}-{rand}"
