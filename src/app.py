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

app = Flask(__name__)
CORS(app)

# Configuración de base de datos
database_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {database_url[:50] if database_url else 'No definida'}...")

if not database_url:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    database_url = f'sqlite:///{os.path.join(data_dir, "tasks.db")}'
    print(f"Usando SQLite: {database_url}")
else:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"URL convertida a: {database_url[:50]}...")
    print("Usando PostgreSQL")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print("✅ SQLAlchemy inicializado correctamente")

# ========== MODELO ==========
class Task(db.Model):
    __tablename__ = 'tasks'
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

# ========== FUNCIÓN PARA INICIALIZAR DB ==========
def init_db():
    try:
        print("🔄 Creando tablas en la base de datos...")
        db.create_all()
        print("✅ Tablas creadas correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        return False

# ========== RUTAS ==========
@app.route('/')
def home():
    """Sirve index.html desde la ubicación correcta"""
    # Lista de posibles ubicaciones
    posibles_ubicaciones = [
        '/app/src/static/index.html',
        '/app/static/index.html',
        'src/static/index.html',
        'static/index.html',
        os.path.join(os.path.dirname(__file__), 'static', 'index.html'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html'),
    ]
    
    print(f"=== BUSCANDO index.html ===")
    for ubicacion in posibles_ubicaciones:
        if os.path.exists(ubicacion):
            print(f"✅ Encontrado en: {ubicacion}")
            # Servir desde la carpeta correcta
            if 'src/static' in ubicacion:
                return send_from_directory('src/static', 'index.html')
            elif 'static' in ubicacion:
                return send_from_directory('static', 'index.html')
            else:
                # Fallback: servir desde el directorio donde está
                directorio = os.path.dirname(ubicacion)
                return send_from_directory(directorio, 'index.html')
    
    # Si no se encuentra, mostrar error detallado
    print("❌ No se encontró index.html en ninguna ubicación")
    print(f"Archivos en /app: {os.listdir('/app') if os.path.exists('/app') else 'No existe'}")
    print(f"Archivos en /app/src: {os.listdir('/app/src') if os.path.exists('/app/src') else 'No existe'}")
    
    return jsonify({
        'error': 'No se encuentra index.html',
        'directorio_actual': os.getcwd(),
        'archivos_en_app': os.listdir('/app') if os.path.exists('/app') else [],
        'archivos_en_src': os.listdir('/app/src') if os.path.exists('/app/src') else [],
    }), 404

@app.route('/static/<path:path>')
def serve_static(path):
    """Sirve archivos estáticos"""
    try:
        if os.path.exists(f'src/static/{path}'):
            return send_from_directory('src/static', path)
        elif os.path.exists(f'static/{path}'):
            return send_from_directory('static', path)
        else:
            return jsonify({'error': f'No se encuentra {path}'}), 404
    except Exception as e:
        print(f"Error en static: {e}")
        return jsonify({'error': str(e)}), 500

# ========== ENDPOINTS API ==========
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()
        return jsonify([t.to_dict() for t in tasks])
    except Exception as e:
        print(f"Error en get_tasks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'El campo "title" es obligatorio'}), 400
        task = Task(title=data['title'], description=data.get('description', ''))
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        print(f"Error en create_task: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    try:
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
    except Exception as e:
        print(f"Error en update_task: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    try:
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Tarea eliminada correctamente'}), 200
    except Exception as e:
        print(f"Error en delete_task: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/healthz')
def health():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'database': 'disconnected', 'error': str(e)}), 500

# ========== INICIALIZAR ==========
init_db()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)