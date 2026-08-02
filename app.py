from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- MODÈLE DE BASE DE DONNÉES ---
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # Date et heure d'enregistrement
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

# --- ROUTE : Récupérer tous les messages avec Jour + Heure ---
@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.asc()).all()
    output = []
    for msg in messages:
        output.append({
            'id': msg.id,
            'sender': msg.sender,
            'message': msg.message,
            # Formatage : Jour/Mois/Année à Heure:Minute (ex: 02/08/2026 à 19:12)
            'datetime_str': msg.timestamp.strftime('%d/%m/%Y à %H:%M') if msg.timestamp else '',
            'likes': msg.likes or 0,
            'dislikes': msg.dislikes or 0
        })
    return jsonify(output)
