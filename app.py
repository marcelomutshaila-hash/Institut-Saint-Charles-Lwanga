from flask import Flask, render_template, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle_secrete_chat'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

# Modèle de la table ChatMessage
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False) # Ex: Nom du visiteur ou "Admin"
    message = db.Column(db.Text, nullable=False)
    expediteur = db.Column(db.String(20), nullable=False) # 'visiteur' ou 'admin'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

# Interface Chat pour les visiteurs
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Interface Chat pour l'administrateur
@app.route('/admin/chat')
def admin_chat():
    return render_template('admin_chat.html')

@app.route('/apropos')
def apropos():
    return render_template('a-propos.html')

@app.route('/formations')
def formations():
    return render_template('formations.html')

@app.route('/actualites')
def actualites():
    return render_template('actualites.html')

# API : Envoyer un message (visiteur ou admin)
@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender_name = data.get('sender_name', 'Visiteur')
    message_text = data.get('message', '')
    expediteur = data.get('expediteur', 'visiteur')

    if message_text.strip():
        msg = ChatMessage(sender_name=sender_name, message=message_text, expediteur=expediteur)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Message vide'}), 400

# API : Récupérer tous les messages (pour rafraîchir le chat en direct)
@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.asc()).all()
    output = []
    for m in messages:
        output.append({
            'id': m.id,
            'sender_name': m.sender_name,
            'message': m.message,
            'expediteur': m.expediteur,
            'time': m.timestamp.strftime('%H:%M')
        })
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
