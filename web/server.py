# web/server.py
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from core.app_core import get_app
from core.schedule_manager import get_schedule_manager
from core.event_manager import get_event_manager
from datetime import datetime, time
from werkzeug.utils import secure_filename
import uuid
import os

app = Flask(__name__)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
app.config['SECRET_KEY'] = 'school-bell-secret'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

bell_app = None
schedule_manager = None
event_manager = None

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('dashboard.html')

# Status
@app.route('/api/status')
def get_status():
    status = bell_app.get_status() if bell_app else {'scheduler': {'running': False}}
    active_profile = schedule_manager.get_active_profile()
    next_bell = status['scheduler'].get('next_bell')
    session = schedule_manager._get_session()
    try:
        from core.models import SchedulerState
        state = session.query(SchedulerState).filter(SchedulerState.id == 1).first()
        is_running = state.is_running if state else False
    finally:
        session.close()
    
    status = bell_app.get_status() if bell_app else {'scheduler': {'running': is_running}}

    # Override with database truth
    status['scheduler']['running'] = is_running
    
    # Get next bell safely
    next_bell_str = None
    if next_bell:
        if hasattr(next_bell, 'tzinfo') and next_bell.tzinfo:
            next_bell = next_bell.replace(tzinfo=None)
        next_bell_str = next_bell.strftime('%H:%M:%S')
    
    return jsonify({
        'scheduler_running': status['scheduler']['running'],
        'active_jobs': status['scheduler']['active_jobs'],
        'active_profile': {
            'id': active_profile.id,
            'name': active_profile.name,
            'description': active_profile.description,
            'is_active': active_profile.is_active
        } if active_profile else None,
        'next_bell': next_bell_str,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# Profiles - FIXED (no lazy loading)
@app.route('/api/profiles')
def get_profiles():
    profiles = schedule_manager.get_all_profiles()
    result = []
    for p in profiles:
        # Get schedule count safely using separate query
        try:
            count = schedule_manager.get_schedule_count_by_profile(p.id)
        except:
            count = 0
        result.append({
            'id': p.id,
            'name': p.name,
            'description': p.description or '',
            'is_active': p.is_active,
            'color': p.color,
            'schedule_count': count
        })
    return jsonify(result)

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    data = request.json
    profile_id = schedule_manager.create_profile(
        name=data['name'],
        description=data.get('description', '')
    )
    if profile_id:
        event_manager.emit('profiles_updated')
        socketio.emit('profiles_updated')
        return jsonify({'success': True, 'id': profile_id})
    return jsonify({'success': False, 'error': 'Failed to create profile'})

@app.route('/api/profiles/<int:profile_id>/activate', methods=['POST'])
def activate_profile(profile_id):
    if schedule_manager.set_active_profile(profile_id):
        if bell_app and bell_app.scheduler.running:
            bell_app.scheduler.reload()
        event_manager.emit('profile_activated', {'profile_id': profile_id})
        event_manager.emit('schedules_reloaded')
        socketio.emit('profile_activated', {'profile_id': profile_id})
        socketio.emit('schedules_updated')
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    active = schedule_manager.get_active_profile()
    if active and active.id == profile_id:
        return jsonify({'success': False, 'error': 'Cannot delete active profile'})
    
    if schedule_manager.delete_profile(profile_id):
        event_manager.emit('profiles_updated')
        socketio.emit('profiles_updated')
        return jsonify({'success': True})
    return jsonify({'success': False})

# Schedules
@app.route('/api/schedules/<int:profile_id>')
def get_schedules(profile_id):
    schedules = schedule_manager.get_schedules_by_profile(profile_id, include_inactive=True)
    return jsonify([s.to_dict() for s in schedules])

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    bell_time = time(int(data['hour']), int(data['minute']))
    schedule_id = schedule_manager.add_schedule(
        profile_id=data['profile_id'],
        name=data['name'],
        bell_time=bell_time,
        days=data.get('days', [0,1,2,3,4]),
        audio_file=data.get('audio_file')
    )
    if schedule_id:
        if bell_app and bell_app.scheduler.running:
            bell_app.scheduler.reload()
        event_manager.emit('schedules_reloaded')
        socketio.emit('schedules_updated')
        return jsonify({'success': True, 'id': schedule_id})
    return jsonify({'success': False})

@app.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    bell_time = time(int(data['hour']), int(data['minute']))
    success = schedule_manager.update_schedule(
        schedule_id,
        name=data['name'],
        bell_time=bell_time,
        days_of_week=','.join(str(d) for d in data.get('days', [0,1,2,3,4])),
        audio_file=data.get('audio_file')
    )
    if success:
        if bell_app and bell_app.scheduler.running:
            bell_app.scheduler.reload()
        event_manager.emit('schedules_reloaded')
        socketio.emit('schedules_updated')
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    success = schedule_manager.delete_schedule(schedule_id)
    if success:
        if bell_app and bell_app.scheduler.running:
            bell_app.scheduler.reload()
        event_manager.emit('schedules_reloaded')
        socketio.emit('schedules_updated')
        return jsonify({'success': True})
    return jsonify({'success': False})

# Audio
@app.route('/api/audio/upload', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not file.filename.lower().endswith(('.mp3', '.wav', '.ogg')):
        return jsonify({'success': False, 'error': 'Invalid audio format'})
    
    # Secure filename with UUID to prevent collision
    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    
    if bell_app:
        audio_dir = bell_app.audio_manager.audio_dir
    else:
        audio_dir = 'assets/audio'
    
    os.makedirs(audio_dir, exist_ok=True)
    filepath = os.path.join(audio_dir, unique_name)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'path': filepath,
        'filename': file.filename,
        'stored_as': unique_name
    })

@app.route('/api/audio/list')
def list_audio():
    audio_dir = 'assets/audio'
    files = []
    if os.path.exists(audio_dir):
        for f in os.listdir(audio_dir):
            if f.endswith(('.mp3', '.wav', '.ogg')):
                files.append({
                    'name': f,
                    'path': os.path.join(audio_dir, f),
                    'size': os.path.getsize(os.path.join(audio_dir, f))
                })
    return jsonify(files)

# Control
@app.route('/api/control/start', methods=['POST'])
def start_system():
    if bell_app:
        if bell_app.scheduler.start():
            # Broadcast to all connected clients
            socketio.emit('system_status', {'running': True})
            event_manager.emit('system_started')
            return jsonify({'success': True, 'message': 'System started'})
        return jsonify({'success': False, 'message': 'Cannot start. No active profile or no schedules.'})
    return jsonify({'success': False, 'message': 'App not initialized'})

@app.route('/api/control/stop', methods=['POST'])
def stop_system():
    if bell_app and bell_app.scheduler.running:
        bell_app.scheduler.stop()
        # Broadcast to all connected clients
        socketio.emit('system_status', {'running': False})
        event_manager.emit('system_stopped')
        return jsonify({'success': True, 'message': 'System stopped'})
    return jsonify({'success': False, 'message': 'System already stopped'})

@app.route('/api/control/ring', methods=['POST'])
def manual_ring():
    data = request.json
    schedule_id = data.get('schedule_id')
    if schedule_id:
        schedule = schedule_manager.get_schedule_by_id(schedule_id)
        if schedule and bell_app:
            bell_app.audio_manager.play(schedule.audio_file)
            return jsonify({'success': True, 'message': f'Ringing {schedule.name}'})
    return jsonify({'success': False, 'message': 'Schedule not found'})

@app.route('/api/control/volume', methods=['POST'])
def set_volume():
    data = request.json
    volume = data.get('volume', 80)
    if bell_app:
        bell_app.audio_manager.set_volume(volume)
        bell_app.config.set('audio.volume', volume)
        return jsonify({'success': True, 'volume': volume})
    return jsonify({'success': False})

# History - FIXED
@app.route('/api/history')
def get_history():
    limit = request.args.get('limit', 50, type=int)
    history = schedule_manager.get_recent_history(limit)
    result = []
    for h in history:
        result.append({
            'id': h.id,
            'schedule_name': h.schedule_name,
            'profile_name': h.profile_name or '-',
            'rang_at': h.rang_at.strftime('%Y-%m-%d %H:%M:%S') if h.rang_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': h.status or 'unknown',
            'audio_played': h.audio_played.split('/')[-1] if h.audio_played else 'default'
        })
    return jsonify(result)

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to School Bell System'})
    # Send current status
    if bell_app:
        status = bell_app.get_status()
        emit('system_status', {'running': status['scheduler']['running']})
        emit('schedules_updated')
        emit('profiles_updated')

# web/server.py (update start_web_server function)
def start_web_server(app_instance, port=5000):
    global bell_app, schedule_manager, event_manager, _events_bound
    bell_app = app_instance
    schedule_manager = bell_app.schedule_manager
    event_manager = get_event_manager()
    
    # Gunakan attribute pada function untuk menyimpan state
    if not hasattr(start_web_server, '_events_bound'):
        start_web_server._events_bound = False
    
    # Prevent duplicate event listeners
    if not start_web_server._events_bound:
        def on_system_started():
            socketio.emit('system_status', {'running': True})
        
        def on_system_stopped():
            socketio.emit('system_status', {'running': False})
        
        def on_scheduler_state_changed(data):
            """Handle scheduler state changes from engine"""
            is_running = data.get('running', False)
            socketio.emit('scheduler_state_changed', {'running': is_running})
            socketio.emit('system_status', {'running': is_running})
        
        def on_schedules_reloaded():
            socketio.emit('schedules_updated')
        
        def on_profiles_updated():
            socketio.emit('profiles_updated')
        
        def on_profile_activated(data):
            socketio.emit('profile_activated', data)
        
        # Register event handlers
        event_manager.on('system_started', on_system_started)
        event_manager.on('system_stopped', on_system_stopped)
        event_manager.on('scheduler_state_changed', on_scheduler_state_changed)  # <-- SEKARANG DEFINED
        event_manager.on('schedules_reloaded', on_schedules_reloaded)
        event_manager.on('profiles_updated', on_profiles_updated)
        event_manager.on('profile_activated', on_profile_activated)
        
        start_web_server._events_bound = True
    
    print("=" * 50)
    print("🌐 Web UI is running!")
    print(f"📍 Open: http://localhost:{port}")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)