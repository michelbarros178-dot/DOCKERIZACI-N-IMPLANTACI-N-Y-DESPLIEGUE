# src/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import sys

print("=== INICIANDO APLICACIÓN ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

app = Flask(__name__, static_folder='../static')
CORS(app)

# Configuración de base de datos
database_url = os.getenv('DATABASE_URL')

print(f"DATABASE_URL: {database_url[:50]}..." if database_url else "DATABASE_URL no definida")

if not database_url:
    # Desarrollo local con SQLite
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    database_url = f'sqlite:///{os.path.join(data_dir, "tasks.db")}'
    print(f"Usando SQLite: {database_url}")
else:
    # PostgreSQL - Render usa postgres:// pero SQLAlchemy espera postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"URL convertida a: {database_url[:50]}...")
    print("Usando PostgreSQL")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy inicializado correctamente")
except Exception as e:
    print(f"❌ Error al inicializar SQLAlchemy: {e}")
    raise

# ========== MODELO ==========
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

# ========== RUTAS ==========
@app.route('/')
def home():
    return send_from_directory('../static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('../static', path)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])

@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get_or_404(id)
    return jsonify(task.to_dict())

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'El campo "title" es obligatorio'}), 400
    task = Task(title=data['title'], description=data.get('description', ''))
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = bool(data['completed'])
    db.session.commit()
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Tarea eliminada correctamente'}), 200

@app.route('/healthz')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)