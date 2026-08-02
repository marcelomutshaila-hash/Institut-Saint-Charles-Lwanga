from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# 1. Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Initialisation de db (OBLIGATOIRE avant de créer les modèles)
db = SQLAlchemy(app)

# 3. Modèle de la base de données
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

# 4. Création automatique des tables
with app.app_context():
    db.create_all()

# --- ROUTES HTML ---
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

# --- API CHAT (MESSAGES, LIKES, DISLIKES, SUPPRESSION) ---
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

@app.route('/api/like_message/<int:msg_id>', methods=['POST'])
def like_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    msg.likes = (msg.likes or 0) + 1
    db.session.commit()
    return jsonify({'status': 'success', 'likes': msg.likes})

@app.route('/api/dislike_message/<int:msg_id>', methods=['POST'])
def dislike_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    msg.dislikes = (msg.dislikes or 0) + 1
    db.session.commit()
    return jsonify({'status': 'success', 'dislikes': msg.dislikes})

@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
