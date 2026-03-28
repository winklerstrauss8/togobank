"""Routes de pages — Sert le frontend."""
from flask import Blueprint, render_template, send_from_directory
import os

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def landing():
    """Page d'accueil publique."""
    return render_template('landing.html')


@pages_bp.route('/app')
@pages_bp.route('/app/<path:path>')
def spa(path=None):
    """Application SPA — toutes les routes client."""
    return render_template('index.html')
