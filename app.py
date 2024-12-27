from flask import Flask, request, jsonify, abort
from datetime import datetime
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Almacenamiento temporal en memoria
tasks = {}
comments = {}
task_counter = 1
comment_counter = 1


@app.route('/tasks', methods=['POST'])
def create_task():
    global task_counter

    data = request.get_json()

    # Crear una nueva tarea
    new_task = {
        'id': task_counter,
        'title': data['title'],
        'description': data['description'],
        'assigned_to': data['assigned_to'],
        'status': 'pending'
    }
    tasks[task_counter] = new_task
    task_counter += 1

    # Enviar notificación
    try:
        notification_data = {
            "email": f"{new_task['assigned_to']}@empresa.com",  # Simulado
            "message": f"Se te ha asignado una nueva tarea: {new_task['title']}\nDescripción: {new_task['description']}"
        }

        # Llamada al servicio de notificación
        requests.post(
            'https://flask-notitication-service.onrender.com',
            json=notification_data
        )
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la notificación: {e}")

    return jsonify(new_task), 201


@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(list(tasks.values()))


@app.route('/tasks/<int:id>/comments', methods=['POST'])
def create_comment(id):
    global comment_counter

    # Verificar si la tarea existe
    if id not in tasks:
        abort(404, description="Tarea no encontrada")

    data = request.get_json()
    if not all(key in data for key in ['user', 'comment']):
        abort(400, description="Faltan campos requeridos")

    # Crear un nuevo comentario
    new_comment = {
        'id': comment_counter,
        'task_id': id,
        'user': data['user'],
        'comment': data['comment'],
        'timestamp': datetime.now().isoformat()
    }
    if id not in comments:
        comments[id] = []
    comments[id].append(new_comment)
    comment_counter += 1

    return jsonify(new_comment), 201


@app.route('/tasks/<int:id>/comments', methods=['GET'])
def get_comments(id):
    # Verificar si la tarea existe
    if id not in tasks:
        abort(404, description="Tarea no encontrada")

    return jsonify(comments.get(id, []))


@app.route('/tasks/<int:id>/status', methods=['PUT'])
def update_task_status(id):
    # Verificar si la tarea existe
    if id not in tasks:
        abort(404, description="Tarea no encontrada")

    task = tasks[id]

    # Cambiar el estado a "completed"
    if task['status'] == 'completed':
        return jsonify({'message': 'La tarea ya está marcada como completada'}), 400

    task['status'] = 'completed'

    return jsonify({
        'id': task['id'],
        'title': task['title'],
        'status': task['status'],
        'message': 'El estado de la tarea se ha actualizado a "completed"'
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
