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
    """Inicializa la base de datos dentro del contexto de la aplicación"""
    try:
        with app.app_context():
            print("🔄 Creando tablas en la base de datos...")
            db.create_all()
            print("✅ Tablas creadas correctamente")
            
            # Verificar que la tabla existe
            from sqlalchemy import text
            with db.engine.connect() as conn:
                # Para PostgreSQL
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                tables = [row[0] for row in result]
                print(f"📋 Tablas existentes: {tables}")
                
                if 'tasks' not in tables:
                    print("⚠️ La tabla 'tasks' no se creó automáticamente. Creando manualmente...")
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(100) NOT NULL,
                            description VARCHAR(200),
                            completed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.commit()
                    print("✅ Tabla 'tasks' creada manualmente")
            
            return True
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        return False

# ========== INICIALIZAR DB AL INICIAR ==========
# Esto se ejecuta cuando la aplicación se carga
with app.app_context():
    print("🔧 Inicializando base de datos...")
    db.create_all()
    print("✅ Base de datos inicializada correctamente")

# ========== RUTAS ==========
@app.route('/')
def home():
    """Sirve index.html desde la ubicación correcta"""
    try:
        # Buscar en varias ubicaciones
        if os.path.exists('src/static/index.html'):
            return send_from_directory('src/static', 'index.html')
        elif os.path.exists('static/index.html'):
            return send_from_directory('static', 'index.html')
        elif os.path.exists('/app/src/static/index.html'):
            return send_from_directory('/app/src/static', 'index.html')
        else:
            # Si no se encuentra, mostrar error
            return jsonify({
                'error': 'No se encuentra index.html',
                'directorio': os.getcwd(),
                'archivos': os.listdir('.') if os.path.exists('.') else []
            }), 404
    except Exception as e:
        print(f"Error en home: {e}")
        return jsonify({'error': str(e)}), 500

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

# ========== PARA DESARROLLO LOCAL ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# ========== PARA RENDER ==========
# La aplicación ya se inicializa al cargar el módulo