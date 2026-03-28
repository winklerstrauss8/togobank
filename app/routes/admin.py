"""Routes Administration — /api/v1/admin."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps

from app import db
from app.models.user import User
from app.models.compte import Compte
from app.models.transaction import Transaction
from app.models.notification import Notification

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Décorateur : accès réservé aux admins."""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') not in ('admin', 'super_admin'):
            return jsonify({'error': 'Accès réservé aux administrateurs'}), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard_stats():
    """KPIs du tableau de bord admin."""
    total_users = User.query.count()
    active_users = User.query.filter_by(statut='actif').count()
    pending_kyc = User.query.filter_by(kyc_valide=False, statut='actif').count()
    total_comptes = Compte.query.count()
    total_transactions = Transaction.query.count()

    total_soldes = db.session.query(db.func.sum(Compte.solde)).scalar() or 0
    total_tx_amount = db.session.query(
        db.func.sum(Transaction.montant)
    ).filter(Transaction.statut == 'valide').scalar() or 0

    recent_tx = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(10).all()

    recent_users = User.query.order_by(
        User.created_at.desc()
    ).limit(10).all()

    return jsonify({
        'kpis': {
            'total_utilisateurs': total_users,
            'utilisateurs_actifs': active_users,
            'kyc_en_attente': pending_kyc,
            'total_comptes': total_comptes,
            'total_transactions': total_transactions,
            'volume_total': total_tx_amount,
            'total_depots': total_soldes,
        },
        'transactions_recentes': [t.to_dict() for t in recent_tx],
        'nouveaux_clients': [u.to_dict() for u in recent_users],
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Liste de tous les utilisateurs."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role')
    statut_filter = request.args.get('statut')

    query = User.query
    if search:
        query = query.filter(
            (User.nom.ilike(f'%{search}%')) |
            (User.prenom.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.numero_client.ilike(f'%{search}%'))
        )
    if role_filter:
        query = query.filter(User.role == role_filter)
    if statut_filter:
        query = query.filter(User.statut == statut_filter)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    }), 200


@admin_bp.route('/users/<user_id>/status', methods=['PATCH'])
@admin_required
def update_user_status(user_id):
    """Modifier le statut d'un utilisateur."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    data = request.get_json()
    new_status = data.get('statut')
    if new_status not in ('actif', 'suspendu', 'bloque'):
        return jsonify({'error': 'Statut invalide'}), 400

    user.statut = new_status
    db.session.commit()

    return jsonify({'message': f'Utilisateur {user.prenom} {user.nom} → {new_status}', 'user': user.to_dict()}), 200


@admin_bp.route('/kyc/<user_id>/validate', methods=['POST'])
@admin_required
def validate_kyc(user_id):
    """Valider le KYC d'un utilisateur."""
    admin_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    from datetime import datetime
    user.kyc_valide = True
    user.kyc_valide_par = admin_id
    user.kyc_valide_le = datetime.utcnow()
    db.session.commit()

    notif = Notification(
        user_id=user.id,
        type='systeme',
        titre='KYC Validé ✅',
        message='Votre dossier KYC a été vérifié et approuvé. Vous bénéficiez maintenant de tous les services TogoBank.'
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({'message': 'KYC validé', 'user': user.to_dict()}), 200


@admin_bp.route('/transactions', methods=['GET'])
@admin_required
def admin_transactions():
    """Toutes les transactions (supervision)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'transactions': [t.to_dict() for t in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    }), 200


@admin_bp.route('/notifications/broadcast', methods=['POST'])
@admin_required
def broadcast_notification():
    """Envoyer une notification à tous les utilisateurs."""
    data = request.get_json()
    users = User.query.filter_by(statut='actif').all()

    for user in users:
        notif = Notification(
            user_id=user.id,
            type='systeme',
            titre=data.get('titre', 'Notification TogoBank'),
            message=data.get('message', '')
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify({'message': f'Notification envoyée à {len(users)} utilisateurs'}), 200
