"""Script de données de démonstration."""
import bcrypt
from datetime import datetime, timedelta, date
import random

from app import db
from app.models.user import User
from app.models.compte import Compte
from app.models.transaction import Transaction
from app.models.carte import CarteBancaire
from app.models.beneficiaire import Beneficiaire
from app.models.notification import Notification
from app.models.recharge import RechargeMobile


def seed_database():
    """Peuple la base avec des données de démonstration."""
    print("🌱 Insertion des données de démonstration...")

    # === ADMIN ===
    admin_hash = bcrypt.hashpw('Admin@2025'.encode(), bcrypt.gensalt()).decode()
    admin = User(
        numero_client='TGB00000001',
        nom='ADMIN',
        prenom='TogoBank',
        email='admin@togobank.tg',
        telephone='90000001',
        password_hash=admin_hash,
        role='super_admin',
        statut='actif',
        kyc_valide=True
    )
    db.session.add(admin)

    # === CLIENT DEMO ===
    client_hash = bcrypt.hashpw('Client@2025'.encode(), bcrypt.gensalt()).decode()
    client = User(
        numero_client='TGB10000001',
        nom='KOFFI',
        prenom='Ama',
        email='ama@example.com',
        telephone='91234567',
        password_hash=client_hash,
        role='client',
        statut='actif',
        type_client='particulier',
        ville='Lomé',
        kyc_valide=True,
        date_naissance=date(1995, 3, 15)
    )
    db.session.add(client)

    # === SECOND CLIENT ===
    client2_hash = bcrypt.hashpw('Client@2025'.encode(), bcrypt.gensalt()).decode()
    client2 = User(
        numero_client='TGB10000002',
        nom='MENSAH',
        prenom='Kofi',
        email='kofi@example.com',
        telephone='92345678',
        password_hash=client2_hash,
        role='client',
        statut='actif',
        type_client='particulier',
        ville='Kara',
        kyc_valide=True,
        date_naissance=date(1990, 7, 22)
    )
    db.session.add(client2)

    db.session.flush()

    # === COMPTES ===
    compte1 = Compte(
        numero_compte='TG001234567890123456',
        user_id=client.id,
        type_compte='courant',
        libelle='Compte Courant Principal',
        solde=1250000.0
    )
    compte_epargne = Compte(
        numero_compte='TG001234567890123457',
        user_id=client.id,
        type_compte='epargne',
        libelle='Épargne Mariage 💍',
        solde=500000.0
    )
    compte2 = Compte(
        numero_compte='TG002345678901234567',
        user_id=client2.id,
        type_compte='courant',
        libelle='Compte Courant',
        solde=750000.0
    )
    db.session.add_all([compte1, compte_epargne, compte2])
    db.session.flush()

    # === CARTES ===
    num, masque, cvv, exp = CarteBancaire.generate_card()
    carte = CarteBancaire(
        compte_id=compte1.id,
        numero_complet=num,
        numero_masque=masque,
        cvv=cvv,
        date_expiration=exp,
        nom_porteur='AMA KOFFI'
    )
    db.session.add(carte)

    # === TRANSACTIONS ===
    types = ['virement', 'recharge', 'frais']
    for i in range(25):
        days_ago = random.randint(0, 60)
        is_credit = random.random() > 0.4
        montant = random.choice([5000, 10000, 25000, 50000, 75000, 100000, 150000])

        tx = Transaction(
            reference=f"TXN-{(datetime.utcnow() - timedelta(days=days_ago)).strftime('%Y%m%d')}-{random.randint(100000, 999999)}",
            compte_source_id=compte2.id if is_credit else compte1.id,
            compte_dest_id=compte1.id if is_credit else compte2.id,
            type_transaction=random.choice(types),
            montant=montant,
            frais=montant * 0.01 if random.random() > 0.5 else 0,
            statut='valide',
            canal=random.choice(['web', 'mobile', 'mixx', 'flooz']),
            description=random.choice([
                'Virement mensuel',
                'Paiement facture',
                'Recharge mobile',
                'Achat en ligne',
                'Salaire',
                'Remboursement',
                'Transfert épargne'
            ]),
            created_at=datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        )
        db.session.add(tx)

    # === BENEFICIAIRES ===
    benef = Beneficiaire(
        user_id=client.id,
        nom='Kofi MENSAH',
        numero_compte=compte2.numero_compte,
        telephone='92345678',
        categorie='amis',
        favori=True
    )
    db.session.add(benef)

    # === NOTIFICATIONS ===
    notifs = [
        ('systeme', 'Bienvenue chez TogoBank Digital ! 🎉', 'Votre compte est activé. Découvrez nos services.'),
        ('transaction', 'Virement reçu 💰', 'Vous avez reçu 150 000 FCFA de Kofi MENSAH.'),
        ('securite', 'Nouvelle connexion 🔒', 'Connexion depuis un nouvel appareil détectée.'),
        ('promotion', 'Offre spéciale 🎁', 'Bénéficiez de 0% de frais sur vos virements ce mois !'),
    ]
    for type_, titre, msg in notifs:
        n = Notification(user_id=client.id, type=type_, titre=titre, message=msg)
        db.session.add(n)

    db.session.commit()
    print("✅ Données de démonstration insérées avec succès !")
    print(f"   👤 Admin : admin@togobank.tg / Admin@2025")
    print(f"   👤 Client 1 : ama@example.com / Client@2025")
    print(f"   👤 Client 2 : kofi@example.com / Client@2025")
