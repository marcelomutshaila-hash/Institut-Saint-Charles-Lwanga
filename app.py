from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- MODÈLE DE BASE DE DONNÉES ---
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)       # Compteur de Likes
    dislikes = db.Column(db.Integer, default=0)    # Compteur de Dislikes

# --- ROUTE : Récupérer tous les messages ---
@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.asc()).all()
    output = []
    for msg in messages:
        output.append({
            'id': msg.id,
            'sender': msg.sender,
            'message': msg.message,
            'time': msg.timestamp.strftime('%H:%M'),
            'likes': msg.likes or 0,
            'dislikes': msg.dislikes or 0
        })
    return jsonify(output)

# --- ROUTE : Aimer un message (+1 Like) ---
@app.route('/api/like_message/<int:msg_id>', methods=['POST'])
def like_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    msg.likes = (msg.likes or 0) + 1
    db.session.commit()
    return jsonify({'status': 'success', 'likes': msg.likes})

# --- ROUTE : Ne pas aimer un message (+1 Dislike) ---
@app.route('/api/dislike_message/<int:msg_id>', methods=['POST'])
def dislike_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    msg.dislikes = (msg.dislikes or 0) + 1
    db.session.commit()
    return jsonify({'status': 'success', 'dislikes': msg.dislikes})

# --- ROUTE : Supprimer un message (Admin) ---
@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'status': 'success'})
