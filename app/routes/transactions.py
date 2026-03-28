"""Routes Transactions — /api/v1/transactions."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from app.models.transaction import Transaction
from app.models.compte import Compte
from app.models.notification import Notification
from app.models.user import User

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('', methods=['GET'])
@jwt_required()
def list_transactions():
    """Historique paginé des transactions."""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    type_filter = request.args.get('type')
    statut_filter = request.args.get('statut')
    search = request.args.get('search')

    # Récupérer les comptes de l'utilisateur
    comptes = Compte.query.filter_by(user_id=user_id).all()
    compte_ids = [c.id for c in comptes]

    query = Transaction.query.filter(
        (Transaction.compte_source_id.in_(compte_ids)) |
        (Transaction.compte_dest_id.in_(compte_ids))
    )

    if type_filter:
        query = query.filter(Transaction.type_transaction == type_filter)
    if statut_filter:
        query = query.filter(Transaction.statut == statut_filter)
    if search:
        query = query.filter(
            (Transaction.description.ilike(f'%{search}%')) |
            (Transaction.reference.ilike(f'%{search}%'))
        )

    query = query.order_by(Transaction.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Enrichir avec la direction (credit/debit)
    results = []
    for t in pagination.items:
        td = t.to_dict()
        td['direction'] = 'credit' if t.compte_dest_id in compte_ids else 'debit'
        results.append(td)

    return jsonify({
        'transactions': results,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    }), 200


@transactions_bp.route('/<transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """Détail d'une transaction."""
    t = Transaction.query.get(transaction_id)
    if not t:
        return jsonify({'error': 'Transaction introuvable'}), 404
    return jsonify({'transaction': t.to_dict()}), 200


@transactions_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    """Initier un virement."""
    user_id = get_jwt_identity()
    data = request.get_json()

    source_id = data.get('compte_source_id')
    dest_identifier = data.get('dest_identifier')  # numéro de compte ou téléphone
    montant = data.get('montant', 0)
    motif = data.get('motif', '')
    description = data.get('description', '')

    if not source_id or not dest_identifier or montant <= 0:
        return jsonify({'error': 'Données de virement invalides'}), 400

    # Vérifier compte source
    source = Compte.query.filter_by(id=source_id, user_id=user_id).first()
    if not source:
        return jsonify({'error': 'Compte source introuvable'}), 404

    if source.statut != 'actif':
        return jsonify({'error': 'Le compte source est suspendu'}), 400

    if source.solde < montant:
        return jsonify({'error': 'Solde insuffisant'}), 400

    if montant > source.plafond_journalier:
        return jsonify({'error': f'Montant dépasse le plafond journalier ({source.plafond_journalier:,.0f} FCFA)'}), 400

    # Rechercher le compte destinataire
    dest = Compte.query.filter_by(numero_compte=dest_identifier).first()
    if not dest:
        # Essayer par téléphone
        dest_user = User.query.filter_by(telephone=dest_identifier).first()
        if dest_user:
            dest = Compte.query.filter_by(user_id=dest_user.id, type_compte='courant').first()

    if not dest:
        return jsonify({'error': 'Compte destinataire introuvable'}), 404

    if dest.statut != 'actif':
        return jsonify({'error': 'Le compte destinataire est suspendu'}), 400

    if source.id == dest.id:
        return jsonify({'error': 'Impossible de virer vers le même compte'}), 400

    # Calculer frais (1% plafonné à 2000 FCFA)
    frais = min(montant * 0.01, 2000.0)
    if source.user_id == dest.user_id:
        frais = 0  # Pas de frais entre ses propres comptes

    # Exécuter le virement
    source.solde -= (montant + frais)
    dest.solde += montant

    # Récupérer noms
    source_user = User.query.get(source.user_id)
    dest_user = User.query.get(dest.user_id)

    transaction = Transaction(
        reference=Transaction.generate_reference(),
        compte_source_id=source.id,
        compte_dest_id=dest.id,
        type_transaction='virement',
        montant=montant,
        frais=frais,
        statut='valide',
        canal='web',
        description=description or f'Virement à {dest_user.prenom} {dest_user.nom}',
        motif=motif,
        ip_source=request.remote_addr,
        date_valeur=datetime.utcnow().date()
    )
    db.session.add(transaction)

    # Notifications
    notif_source = Notification(
        user_id=source.user_id,
        type='transaction',
        titre='Virement envoyé 💸',
        message=f'Virement de {montant:,.0f} FCFA vers {dest_user.prenom} {dest_user.nom} effectué. Réf: {transaction.reference}'
    )
    notif_dest = Notification(
        user_id=dest.user_id,
        type='transaction',
        titre='Virement reçu 💰',
        message=f'Vous avez reçu {montant:,.0f} FCFA de {source_user.prenom} {source_user.nom}. Réf: {transaction.reference}'
    )
    db.session.add(notif_source)
    db.session.add(notif_dest)

    db.session.commit()

    return jsonify({
        'message': 'Virement effectué avec succès',
        'transaction': transaction.to_dict(),
        'frais': frais,
        'nouveau_solde': source.solde
    }), 201


@transactions_bp.route('/stats', methods=['GET'])
@jwt_required()
def transaction_stats():
    """Statistiques de transactions pour les graphiques."""
    user_id = get_jwt_identity()
    comptes = Compte.query.filter_by(user_id=user_id).all()
    compte_ids = [c.id for c in comptes]

    # Transactions récentes
    recent = Transaction.query.filter(
        (Transaction.compte_source_id.in_(compte_ids)) |
        (Transaction.compte_dest_id.in_(compte_ids))
    ).order_by(Transaction.created_at.desc()).limit(30).all()

    total_credits = sum(t.montant for t in recent if t.compte_dest_id in compte_ids and t.statut == 'valide')
    total_debits = sum(t.montant for t in recent if t.compte_source_id in compte_ids and t.statut == 'valide')

    return jsonify({
        'total_credits': total_credits,
        'total_debits': total_debits,
        'nb_transactions': len(recent),
        'transactions_recentes': [
            {
                **t.to_dict(),
                'direction': 'credit' if t.compte_dest_id in compte_ids else 'debit'
            } for t in recent[:10]
        ]
    }), 200
