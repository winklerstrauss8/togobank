"""Routes Comptes Bancaires — /api/v1/accounts."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.compte import Compte
from app.models.carte import CarteBancaire
from app.models.user import User

accounts_bp = Blueprint('accounts', __name__)


@accounts_bp.route('', methods=['GET'])
@jwt_required()
def list_accounts():
    """Liste des comptes de l'utilisateur."""
    user_id = get_jwt_identity()
    comptes = Compte.query.filter_by(user_id=user_id).all()
    return jsonify({
        'comptes': [c.to_dict() for c in comptes],
        'total_solde': sum(c.solde for c in comptes)
    }), 200


@accounts_bp.route('/<account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    """Détail d'un compte."""
    user_id = get_jwt_identity()
    compte = Compte.query.filter_by(id=account_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404

    carte = CarteBancaire.query.filter_by(compte_id=compte.id).first()
    return jsonify({
        'compte': compte.to_dict(),
        'carte': carte.to_dict() if carte else None
    }), 200


@accounts_bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    """Ouverture d'un nouveau compte."""
    user_id = get_jwt_identity()
    data = request.get_json()

    type_compte = data.get('type_compte', 'courant')
    if type_compte not in ('courant', 'epargne', 'pro', 'jeune'):
        return jsonify({'error': 'Type de compte invalide'}), 400

    compte = Compte(
        numero_compte=Compte.generate_numero_compte(),
        user_id=user_id,
        type_compte=type_compte,
        libelle=data.get('libelle')
    )
    db.session.add(compte)
    db.session.commit()

    return jsonify({
        'message': 'Compte créé avec succès',
        'compte': compte.to_dict()
    }), 201


@accounts_bp.route('/<account_id>', methods=['PATCH'])
@jwt_required()
def update_account(account_id):
    """Mise à jour d'un compte (libellé, plafonds)."""
    user_id = get_jwt_identity()
    compte = Compte.query.filter_by(id=account_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404

    data = request.get_json()
    if 'libelle' in data:
        compte.libelle = data['libelle']
    if 'plafond_journalier' in data:
        compte.plafond_journalier = float(data['plafond_journalier'])
    if 'plafond_mensuel' in data:
        compte.plafond_mensuel = float(data['plafond_mensuel'])

    db.session.commit()
    return jsonify({'compte': compte.to_dict(), 'message': 'Compte mis à jour'}), 200


@accounts_bp.route('/<account_id>/block', methods=['POST'])
@jwt_required()
def block_account(account_id):
    """Blocage/déblocage d'un compte."""
    user_id = get_jwt_identity()
    compte = Compte.query.filter_by(id=account_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404

    compte.statut = 'suspendu' if compte.statut == 'actif' else 'actif'
    db.session.commit()

    action = 'bloqué' if compte.statut == 'suspendu' else 'débloqué'
    return jsonify({'message': f'Compte {action}', 'compte': compte.to_dict()}), 200


@accounts_bp.route('/<account_id>/card', methods=['GET'])
@jwt_required()
def get_card(account_id):
    """Récupérer la carte associée au compte."""
    user_id = get_jwt_identity()
    compte = Compte.query.filter_by(id=account_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404

    carte = CarteBancaire.query.filter_by(compte_id=compte.id).first()
    if not carte:
        return jsonify({'error': 'Aucune carte associée'}), 404

    show_full = request.args.get('full', 'false') == 'true'
    return jsonify({'carte': carte.to_dict(show_full=show_full)}), 200


@accounts_bp.route('/<account_id>/card/toggle', methods=['POST'])
@jwt_required()
def toggle_card(account_id):
    """Bloquer/débloquer la carte bancaire."""
    user_id = get_jwt_identity()
    compte = Compte.query.filter_by(id=account_id, user_id=user_id).first()
    if not compte:
        return jsonify({'error': 'Compte introuvable'}), 404

    carte = CarteBancaire.query.filter_by(compte_id=compte.id).first()
    if not carte:
        return jsonify({'error': 'Aucune carte associée'}), 404

    carte.statut = 'bloquee' if carte.statut == 'active' else 'active'
    db.session.commit()

    action = 'bloquée' if carte.statut == 'bloquee' else 'activée'
    return jsonify({'message': f'Carte {action}', 'carte': carte.to_dict()}), 200
