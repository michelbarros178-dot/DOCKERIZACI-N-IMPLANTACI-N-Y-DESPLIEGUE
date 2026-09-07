import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS PARA TU ESTRUCTURA DE CARPETAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Le decimos a Flask que la carpeta 'static' está en src/static
# Y usamos esa misma carpeta como 'templates' porque tu index.html está ahí.
app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, 'static'), 
            template_folder=os.path.join(BASE_DIR, 'static'))

# --- CONFIGURACIÓN DE LA BASE DE DATOS (PostgreSQL) ---
# Usa la variable de entorno que ya tienes en Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DEFINICIÓN DEL MODELO (TABLA DE TAREAS) ---
class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(200), nullable=False)
    completada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'contenido': self.contenido,
            'completada': self.completada,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

# --- CORRECCIÓN DEL ERROR 404 (CARGAR EL FRONTEND) ---
@app.route('/')
def home():
    # Busca y carga el archivo index.html que está en src/static
    return render_template('index.html')

# Ruta para servir los archivos estáticos (CSS y JS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# --- RUTAS DE LA API (CRUD DE TAREAS) ---

# 1. Obtener todas las tareas
@app.route('/api/tareas', methods=['GET'])
def get_tareas():
    tareas = Tarea.query.order_by(Tarea.id.asc()).all()
    return jsonify([tarea.to_dict() for tarea in tareas])

# 2. Crear una nueva tarea
@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    data = request.get_json()
    if not data or 'contenido' not in data:
        return jsonify({'error': 'El campo "contenido" es obligatorio'}), 400
    
    nueva_tarea = Tarea(contenido=data['contenido'])
    db.session.add(nueva_tarea)
    db.session.commit()
    return jsonify(nueva_tarea.to_dict()), 201

# 3. Actualizar una tarea (marcar como completada o editar texto)
@app.route('/api/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    data = request.get_json()
    
    if 'contenido' in data:
        tarea.contenido = data['contenido']
    if 'completada' in data:
        tarea.completada = data['completada']
        
    db.session.commit()
    return jsonify(tarea.to_dict())

# 4. Eliminar una tarea
@app.route('/api/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    return jsonify({'mensaje': 'Tarea eliminada correctamente'}), 200

# --- RUTA DE SALUD (para verificar que no vuelva a salir el error 404 en logs) ---
@app.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "ok", "database": "conectada", "app": "Funcionando"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- ARRANQUE DE LA APLICACIÓN ---
if __name__ == '__main__':
    # Render asigna automáticamente el puerto
    port = int(os.environ.get('PORT', 5000))
    
    # Creamos las tablas si no existen (solo por si acaso no usaste migraciones)
    with app.app_context():
        db.create_all()
        
    app.run(host='0.0.0.0', port=port)