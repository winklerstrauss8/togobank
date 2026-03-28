"""Routes Recharge Mobile Money — /api/v1/topup."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
import re

from app import db
from app.models.recharge import RechargeMobile
from app.models.compte import Compte
from app.models.transaction import Transaction
from app.models.notification import Notification

topup_bp = Blueprint('topup', __name__)


def validate_phone_mixx(phone):
    """Valide un numéro Moov (9XXXXXXXX)."""
    return bool(re.match(r'^9\d{7}$', phone))


def validate_phone_flooz(phone):
    """Valide un numéro Togocom (7 ou 8 + 7 chiffres)."""
    return bool(re.match(r'^[78]\d{7}$', phone))


@topup_bp.route('/mixx/initiate', methods=['POST'])
@jwt_required()
def initiate_mixx():
    """Initier une recharge via Mixx By Yas (Moov Togo)."""
    user_id = get_jwt_identity()
    data = request.get_json()

    compte_id = data.get('compte_id')
    numero_tel = data.get('numero_tel', '').strip()
    montant = data.get('montant', 0)

    # Validations
    if not validate_phone_mixx(numero_tel):
        return jsonify({'error': 'Numéro Moov invalide. Format attendu : 9XXXXXXX'}), 400

    if montant < 500:
        return jsonify({'error': 'Montant minimum : 500 FCFA'}), 400
    if montant > 200000:
        return jsonify({'error': 'Montant maximum : 200 000 FCFA par recharge'}), 400

    compte = Compte.query.filter_by(id=compte_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404
    if compte.statut != 'actif':
        return jsonify({'error': 'Compte suspendu. Recharge impossible.'}), 400

    # Créer la recharge
    ref = f"MXX-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    recharge = RechargeMobile(
        compte_id=compte_id,
        operateur='mixx',
        numero_tel=numero_tel,
        montant=montant,
        reference_interne=ref,
        statut='en_cours'
    )
    db.session.add(recharge)
    db.session.commit()

    # En mode mock : simuler le succès après 2s côté frontend
    return jsonify({
        'message': 'Recharge initiée. Confirmez sur votre téléphone Moov.',
        'recharge': recharge.to_dict(),
        'mock_mode': True,
        'instructions': 'En mode démo, la recharge sera automatiquement validée.'
    }), 201


@topup_bp.route('/flooz/initiate', methods=['POST'])
@jwt_required()
def initiate_flooz():
    """Initier une recharge via Flooz (Togocom)."""
    user_id = get_jwt_identity()
    data = request.get_json()

    compte_id = data.get('compte_id')
    numero_tel = data.get('numero_tel', '').strip()
    montant = data.get('montant', 0)

    if not validate_phone_flooz(numero_tel):
        return jsonify({'error': 'Numéro Togocom invalide. Format attendu : 7XXXXXXX ou 8XXXXXXX'}), 400

    if montant < 500:
        return jsonify({'error': 'Montant minimum : 500 FCFA'}), 400
    if montant > 150000:
        return jsonify({'error': 'Montant maximum : 150 000 FCFA par recharge'}), 400

    compte = Compte.query.filter_by(id=compte_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404
    if compte.statut != 'actif':
        return jsonify({'error': 'Compte suspendu. Recharge impossible.'}), 400

    ref = f"FLZ-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    recharge = RechargeMobile(
        compte_id=compte_id,
        operateur='flooz',
        numero_tel=numero_tel,
        montant=montant,
        reference_interne=ref,
        statut='en_cours'
    )
    db.session.add(recharge)
    db.session.commit()

    return jsonify({
        'message': 'Recharge initiée. Confirmez sur votre téléphone Togocom.',
        'recharge': recharge.to_dict(),
        'mock_mode': True,
        'instructions': 'En mode démo, la recharge sera automatiquement validée.'
    }), 201


@topup_bp.route('/confirm/<recharge_id>', methods=['POST'])
@jwt_required()
def confirm_topup(recharge_id):
    """Confirmer une recharge (simulation mock)."""
    user_id = get_jwt_identity()
    recharge = RechargeMobile.query.get(recharge_id)
    if not recharge:
        return jsonify({'error': 'Recharge introuvable'}), 404

    if recharge.statut != 'en_cours':
        return jsonify({'error': 'Cette recharge a déjà été traitée'}), 400

    compte = Compte.query.get(recharge.compte_id)
    if not compte or compte.user_id != user_id:
        return jsonify({'error': 'Non autorisé'}), 403

    # Créditer le compte
    compte.solde += recharge.montant
    recharge.statut = 'valide'
    recharge.reference_externe = f"EXT-{str(uuid.uuid4())[:12].upper()}"

    # Créer la transaction
    tx = Transaction(
        reference=Transaction.generate_reference(),
        compte_dest_id=compte.id,
        type_transaction='recharge',
        montant=recharge.montant,
        statut='valide',
        canal=recharge.operateur,
        description=f'Recharge {recharge.operateur.upper()} depuis {recharge.numero_tel}',
        motif='Recharge mobile money',
        date_valeur=datetime.utcnow().date()
    )
    db.session.add(tx)

    # Notification
    operateur_label = 'Mixx By Yas' if recharge.operateur == 'mixx' else 'Flooz'
    notif = Notification(
        user_id=user_id,
        type='transaction',
        titre=f'Recharge {operateur_label} réussie ✅',
        message=f'Votre compte a été crédité de {recharge.montant:,.0f} FCFA via {operateur_label}.'
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        'message': f'Recharge de {recharge.montant:,.0f} FCFA validée !',
        'recharge': recharge.to_dict(),
        'nouveau_solde': compte.solde
    }), 200


@topup_bp.route('/history', methods=['GET'])
@jwt_required()
def topup_history():
    """Historique des recharges mobile."""
    user_id = get_jwt_identity()
    comptes = Compte.query.filter_by(user_id=user_id).all()
    compte_ids = [c.id for c in comptes]

    recharges = RechargeMobile.query.filter(
        RechargeMobile.compte_id.in_(compte_ids)
    ).order_by(RechargeMobile.created_at.desc()).limit(50).all()

    return jsonify({
        'recharges': [r.to_dict() for r in recharges]
    }), 200
