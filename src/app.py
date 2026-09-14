import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS PARA TU ESTRUCTURA DE CARPETAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Asegurar que la carpeta 'data' exista dentro del contenedor
data_dir = os.path.join(ROOT_DIR, 'data')
os.makedirs(data_dir, exist_ok=True)

db_path = os.path.join(data_dir, 'tasks.db')

app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, 'static'), 
            template_folder=os.path.join(BASE_DIR, 'static'))

# --- CONFIGURACIÓN DE LA BASE DE DATOS (SQLite) ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DEFINICIÓN DEL MODELO (TABLA DE TAREAS) ---
class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(200), nullable=False)
    completada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        fecha_str = self.fecha_creacion.isoformat() if self.fecha_creacion else datetime.utcnow().isoformat()
        return {
            'id': self.id,
            'contenido': self.contenido,
            'title': self.contenido,         # Compatible si el JS busca 'title'
            'text': self.contenido,          # Compatible si el JS busca 'text'
            'completada': self.completada,
            'completed': self.completada,    # Compatible si el JS busca 'completed'
            'fecha_creacion': fecha_str,
            'created_at': fecha_str          # Compatible si el JS busca 'created_at'
        }

# --- CARGAR EL FRONTEND ---
@app.route('/')
def home():
    nombre_nodo = os.environ.get('NODO_NAME', 'Nodo A')
    return render_template('index.html', nombre_nodo=nombre_nodo)

# --- RUTAS DE LA API (CRUD DE TAREAS) ---

# 1. Obtener todas las tareas
@app.route('/api/tasks', methods=['GET'])
def get_tareas():
    tareas = Tarea.query.order_by(Tarea.id.asc()).all()
    return jsonify([tarea.to_dict() for tarea in tareas])

# 2. Crear una nueva tarea (Soporta 'contenido' o 'title')
@app.route('/api/tasks', methods=['POST'])
def crear_tarea():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos no válidos'}), 400
    
    texto_tarea = data.get('contenido') or data.get('title') or data.get('text')
    
    if not texto_tarea:
        return jsonify({'error': 'El campo de texto es obligatorio'}), 400
    
    nueva_tarea = Tarea(contenido=texto_tarea)
    db.session.add(nueva_tarea)
    db.session.commit()
    return jsonify(nueva_tarea.to_dict()), 201

# 3. Actualizar una tarea (Soporta múltiples variaciones de campos)
@app.route('/api/tasks/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos no válidos'}), 400
    
    nuevo_contenido = data.get('contenido') or data.get('title') or data.get('text')
    if nuevo_contenido is not None:
        tarea.contenido = nuevo_contenido
        
    nueva_completada = data.get('completada') if 'completada' in data else data.get('completed')
    if nueva_completada is not None:
        tarea.completada = nueva_completada
        
    db.session.commit()
    return jsonify(tarea.to_dict())

# 4. Eliminar una tarea
@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    return jsonify({'mensaje': 'Tarea eliminada correctamente'}), 200

# --- RUTA DE SALUD ---
@app.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "ok", "database": "conectada", "app": "Funcionando"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- RUTA COMODÍN PARA ARCHIVOS ESTÁTICOS ---
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# --- ARRANQUE DE LA APLICACIÓN ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    with app.app_context():
        db.create_all()
        
    app.run(host='0.0.0.0', port=port)