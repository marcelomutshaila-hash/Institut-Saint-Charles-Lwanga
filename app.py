import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'

# --- GESTION DE LA BASE DE DONNÉES ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///chat.db')

# Correction du préfixe postgres:// pour SQLAlchemy
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLE DE BASE DE DONNÉES ---
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auteur = db.Column(db.String(100), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    
    # ID du message auquel on répond (None s'il s'agit d'un message principal)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    
    # Relation d'imbrication pour récupérer les réponses
    reponses = db.relationship('Message', backref=db.backref('parent', remote_side=[id]), cascade="all, delete-orphan")

# Création des tables
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/a-propos')
def a_propos():
    return render_template('a-propos.html')

@app.route('/formations')
def formations():
    return render_template('formations.html')

@app.route('/actualites')
def actualites():
    return render_template('actualites.html')

# Route Contact (gère l'affichage ET l'envoi des messages)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        auteur = request.form.get('auteur')
        contenu = request.form.get('contenu')
        
        if auteur and contenu:
            nouveau_message = Message(auteur=auteur, contenu=contenu)
            db.session.add(nouveau_message)
            db.session.commit()
            flash("Votre message a été envoyé avec succès !", "success")
            return redirect(url_for('contact'))

    messages = Message.query.filter_by(parent_id=None).order_by(Message.date_creation.desc()).all()
    return render_template('contact.html', messages=messages)

# Route du Chat Public
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        auteur = request.form.get('auteur')
        contenu = request.form.get('contenu')
        if auteur and contenu:
            nouveau_message = Message(auteur=auteur, contenu=contenu)
            db.session.add(nouveau_message)
            db.session.commit()
            return redirect(url_for('chat'))
            
    messages = Message.query.filter_by(parent_id=None).order_by(Message.date_creation.desc()).all()
    return render_template('chat.html', messages=messages)

# Route du Panneau d'Administration / Modération
@app.route('/admin')
def admin_panel():
    messages = Message.query.filter_by(parent_id=None).order_by(Message.date_creation.desc()).all()
    return render_template('admin_chat.html', messages=messages)

# Route pour Répondre directement à un message (Admin)
@app.route('/repondre/<int:message_id>', methods=['POST'])
def repondre(message_id):
    contenu = request.form.get('contenu')
    if contenu:
        nouvelle_reponse = Message(
            auteur="Administrateur",
            contenu=contenu,
            parent_id=message_id
        )
        db.session.add(nouvelle_reponse)
        db.session.commit()
    return redirect(url_for('admin_panel'))

# Route de Suppression d'un message
@app.route('/supprimer/<int:id>')
def supprimer(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
