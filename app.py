from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION BASE DE DONNÉES ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLE DE BASE DE DONNÉES ---
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

# Création des tables SQLite au démarrage
with app.app_context():
    db.create_all()

# --- ROUTES DE NAVIGATION ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/apropos')
def apropos():
    return render_template('a-propos.html')

@app.route('/formations')
def formations():
    return render_template('formations.html')

@app.route('/actualites')
def actualites():
    return render_template('actualites.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin/chat')
def admin_chat():
    return render_template('admin_chat.html')

# --- ROUTES API (CHAT EN DIRECT) ---

# 1. Récupérer tous les messages avec Jour + Heure
@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.asc()).all()
    output = []
    for msg in messages:
        output.append({
            'id': msg.id,
            'sender': msg.sender,
            'message': msg.message,
            'datetime_str': msg.timestamp.strftime('%d/%m/%Y à %H:%M') if msg.timestamp else '',
            'likes': msg.likes or 0,
            'dislikes': msg.dislikes or 0
        })
    return jsonify(output)

# 2. Envoyer un message (Visiteur ou Admin)
@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'status': 'error', 'message': 'Message vide'}), 400
        
    new_msg = ChatMessage(
        sender=data.get('sender', 'Visiteur'),
        message=data.get('message')
    )
    db.session.add(new_msg)
    db.session.commit()
    return jsonify({'status': 'success'})

# 3. Aimer un message (+1 Like)
@app.route('/api/like_message/<int:msg_id>', methods=['POST'])
def like_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    msg.likes = (msg.likes or 0) + 1
    db.session.commit()
    return jsonify({'status': 'success', 'likes': msg.likes})

# 4. Ne pas aimer un message (+1 Dislike)
@app.route('/api/dislike_message/<int:msg_id>', methods=['POST'])
def dislike_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    msg.dislikes = (msg.dislikes or 0) + 1
    db.session.commit()
    return jsonify({'status': 'success', 'dislikes': msg.dislikes})

# 5. Supprimer un message (Admin)
@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'status': 'success'})

# --- DÉMARRAGE DU SERVEUR ---
if __name__ == '__main__':
    app.run(debug=True)
