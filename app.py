import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('chat_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            datetime_str TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Exécution obligatoire au démarrage
init_db()


# --- ROUTES HTML POUR LES PAGES ---

@app.route('/')
@app.route('/index')
def page_accueil():
    return render_template('index.html')

@app.route('/contact')
@app.route('/contact.html')
def page_contact():
    return render_template('contact.html')

@app.route('/admin/chat')
@app.route('/admin_chat')
@app.route('/admin_chat.html')
def page_admin_chat():
    return render_template('admin_chat.html')


# --- API DU TCHAT ---

# 1. Récupérer les messages
@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    try:
        conn = sqlite3.connect('chat_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY id ASC')
        rows = cursor.fetchall()
        conn.close()
        
        messages = [dict(row) for row in rows]
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. Envoyer un message
@app.route('/api/send_message', methods=['POST'])
def send_message():
    try:
        data = request.json
        sender = data.get('sender', 'Visiteur').strip() or 'Visiteur'
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
            
        datetime_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
        
        conn = sqlite3.connect('chat_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (sender, message, datetime_str, likes, dislikes)
            VALUES (?, ?, ?, 0, 0)
        ''', (sender, message, datetime_str))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. Supprimer un message (RESERVÉ À L'ADMINISTRATION)
@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    try:
        conn = sqlite3.connect('chat_database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. Reaction : Like
@app.route('/api/like_message/<int:msg_id>', methods=['POST'])
def like_message(msg_id):
    try:
        conn = sqlite3.connect('chat_database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE messages SET likes = likes + 1 WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 5. Reaction : Dislike
@app.route('/api/dislike_message/<int:msg_id>', methods=['POST'])
def dislike_message(msg_id):
    try:
        conn = sqlite3.connect('chat_database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE messages SET dislikes = dislikes + 1 WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
