# web/server.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from core.app_core import SchoolBellApp
import threading
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'school-bell-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global app instance
bell_app = None

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    schedules = bell_app.db_manager.get_all_schedules()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'hour': s.hour,
        'minute': s.minute,
        'days': s.days_of_week,
        'is_active': s.is_active,
        'audio_file': s.audio_file
    } for s in schedules])

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    schedule_id = bell_app.db_manager.add_schedule(
        name=data['name'],
        hour=data['hour'],
        minute=data['minute'],
        days_of_week=data.get('days'),
        audio_file=data.get('audio_file')
    )
    bell_app.scheduler.reload_schedules()
    socketio.emit('schedule_updated', {'action': 'add', 'id': schedule_id})
    return jsonify({'success': True, 'id': schedule_id})

@app.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    success = bell_app.db_manager.update_schedule(schedule_id, **data)
    if success:
        bell_app.scheduler.reload_schedules()
        socketio.emit('schedule_updated', {'action': 'update', 'id': schedule_id})
    return jsonify({'success': success})

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    success = bell_app.db_manager.delete_schedule(schedule_id)
    if success:
        bell_app.scheduler.reload_schedules()
        socketio.emit('schedule_updated', {'action': 'delete', 'id': schedule_id})
    return jsonify({'success': success})

@app.route('/api/status', methods=['GET'])
def get_status():
    status = bell_app.get_status()
    return jsonify(status)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected to School Bell System'})

def start_web_server(app_instance, port=5000):
    global bell_app
    bell_app = app_instance
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)