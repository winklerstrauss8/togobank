"""Routes d'authentification — /api/v1/auth."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import bcrypt

from app import db, limiter
from app.models.user import User
from app.models.compte import Compte
from app.models.notification import Notification
from app.models.carte import CarteBancaire

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5/minute")
def register():
    """Inscription d'un nouvel utilisateur."""
    data = request.get_json()

    # Validation
    required = ['nom', 'prenom', 'email', 'telephone', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Le champ {field} est obligatoire'}), 400

    # Vérification unicité
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cet email est déjà utilisé'}), 409
    if User.query.filter_by(telephone=data['telephone']).first():
        return jsonify({'error': 'Ce numéro de téléphone est déjà utilisé'}), 409

    # Création utilisateur
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        numero_client=User.generate_numero_client(),
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        telephone=data['telephone'],
        password_hash=password_hash,
        type_client=data.get('type_client', 'particulier'),
        date_naissance=data.get('date_naissance'),
        ville=data.get('ville'),
        adresse=data.get('adresse'),
        statut='actif'  # En dev, actif directement
    )
    db.session.add(user)
    db.session.flush()  # Générer user.id

    # Créer un compte courant par défaut
    compte = Compte(
        numero_compte=Compte.generate_numero_compte(),
        user_id=user.id,
        type_compte='courant',
        libelle='Compte Courant Principal',
        solde=50000.0  # Bonus de bienvenue en dev
    )
    db.session.add(compte)
    db.session.flush()  # Générer compte.id

    # Générer une carte virtuelle
    numero, masque, cvv, exp = CarteBancaire.generate_card()
    carte = CarteBancaire(
        compte_id=compte.id,
        numero_complet=numero,
        numero_masque=masque,
        cvv=cvv,
        date_expiration=exp,
        nom_porteur=f"{user.prenom.upper()} {user.nom.upper()}"
    )
    db.session.add(carte)

    # Notification de bienvenue
    notif = Notification(
        user_id=user.id,
        type='systeme',
        titre='Bienvenue chez TogoBank Digital ! 🎉',
        message=f'Votre compte a été créé avec succès. Numéro client : {user.numero_client}. Un bonus de 50 000 FCFA a été crédité.'
    )
    db.session.add(notif)

    db.session.commit()

    # Générer tokens
    access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Inscription réussie ! Bienvenue chez TogoBank.',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10/minute")
def login():
    """Connexion utilisateur."""
    data = request.get_json()
    identifier = data.get('email') or data.get('telephone')
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'error': 'Email/téléphone et mot de passe requis'}), 400

    # Recherche par email ou téléphone
    user = User.query.filter(
        (User.email == identifier) | (User.telephone == identifier)
    ).first()

    if not user:
        return jsonify({'error': 'Identifiants incorrects'}), 401

    # Vérifier blocage
    if user.bloque_jusqu_au and user.bloque_jusqu_au > datetime.utcnow():
        remaining = (user.bloque_jusqu_au - datetime.utcnow()).seconds // 60
        return jsonify({'error': f'Compte temporairement bloqué. Réessayez dans {remaining} minutes.'}), 423

    # Vérifier mot de passe
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        user.tentatives_connexion += 1
        if user.tentatives_connexion >= 5:
            user.bloque_jusqu_au = datetime.utcnow() + timedelta(minutes=15)
            user.tentatives_connexion = 0
            db.session.commit()
            return jsonify({'error': 'Trop de tentatives. Compte bloqué pendant 15 minutes.'}), 423
        db.session.commit()
        return jsonify({'error': 'Identifiants incorrects'}), 401

    if user.statut != 'actif':
        return jsonify({'error': f'Votre compte est {user.statut}. Contactez le support.'}), 403

    # Succès — réinitialiser tentatives
    user.tentatives_connexion = 0
    user.derniere_connexion = datetime.utcnow()
    db.session.commit()

    access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Connexion réussie',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renouvellement du token JWT."""
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    access_token = create_access_token(identity=identity, additional_claims={'role': user.role})
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Profil de l'utilisateur connecté."""
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_me():
    """Mise à jour du profil."""
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    updatable = ['nom', 'prenom', 'ville', 'adresse', 'langue', 'notification_email', 'notification_sms']
    for field in updatable:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify({'user': user.to_dict(), 'message': 'Profil mis à jour'}), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Changement de mot de passe."""
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    if not bcrypt.checkpw(data['current_password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Mot de passe actuel incorrect'}), 400

    user.password_hash = bcrypt.hashpw(data['new_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()

    return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
