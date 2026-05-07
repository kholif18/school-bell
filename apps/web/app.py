# apps/web/app.py
from flask import Flask, jsonify, render_template, request
import json
import os
from werkzeug.utils import secure_filename

# Konfigurasi upload
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "assets", "audio")
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_web_app(core):
    """
    Web UI layer untuk School Bell System
    - CoreApp sebagai backend single source of truth
    - Flask hanya sebagai interface
    """

    app = Flask(__name__)

    # =========================================================
    # WEB UI PAGE
    # =========================================================
    @app.route("/")
    def index():
        return render_template("index.html")

    # =========================================================
    # STATUS SYSTEM
    # =========================================================
    @app.route("/api/status")
    def status():
        try:
            return jsonify({
                "ok": True,
                "data": core.get_status()
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    # =========================================================
    # START SYSTEM
    # =========================================================
    @app.route("/api/start", methods=["POST"])
    def start():
        try:
            core.start_system()
            return jsonify({
                "ok": True,
                "state": "started"
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    # =========================================================
    # STOP SYSTEM
    # =========================================================
    @app.route("/api/stop", methods=["POST"])
    def stop():
        try:
            core.stop_system()
            return jsonify({
                "ok": True,
                "state": "stopped"
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    # =========================================================
    # RELOAD SYSTEM
    # =========================================================
    @app.route("/api/reload", methods=["POST"])
    def reload():
        try:
            core.reload_system()
            return jsonify({
                "ok": True,
                "state": "reloaded"
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    # =========================================================
    # TEST BELL
    # =========================================================
    @app.route("/api/test-bell", methods=["POST"])
    def test_bell():
        try:
            data = request.get_json() or {}
            audio_file = data.get("audio_file")
            core.test_audio(audio_file)
            return jsonify({
                "ok": True,
                "message": "test bell triggered"
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500
        
    @app.route('/api/stop-bell', methods=['POST'])
    def stop_bell():
        try:
            bell_service.stop()

            return jsonify({
                'ok': True,
                'message': 'Bell stopped'
            })

        except Exception as e:
            return jsonify({
                'ok': False,
                'error': str(e)
            }), 500

    # =========================================================
    # PROFILE CRUD
    # =========================================================
    @app.route("/api/profiles")
    def get_profiles():
        try:
            profiles = core.get_profiles()
            active_profile = core.get_active_profile()
            
            return jsonify({
                "ok": True,
                "data": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": getattr(p, 'description', ''),
                        "color": getattr(p, 'color', '#4CAF50'),
                        "is_active": p.id == active_profile.id if active_profile else False,
                        "schedule_count": len(core.get_schedules(p.id))
                    }
                    for p in profiles
                ]
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/profiles", methods=["POST"])
    def create_profile():
        try:
            data = request.get_json()
            name = data.get("name")
            description = data.get("description", "")
            color = data.get("color", "#4CAF50")
            
            if not name:
                return jsonify({"ok": False, "error": "Name required"}), 400
            
            profile_id = core.create_profile(name, description, color)
            
            return jsonify({
                "ok": True,
                "data": {"id": profile_id, "name": name}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/profiles/<int:profile_id>", methods=["PUT"])
    def update_profile(profile_id):
        try:
            data = request.get_json()
            result = core.update_profile(
                profile_id,
                name=data.get("name"),
                description=data.get("description"),
                color=data.get("color")
            )
            
            return jsonify({
                "ok": True,
                "data": {"id": profile_id, "updated": result}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/profiles/<int:profile_id>", methods=["DELETE"])
    def delete_profile(profile_id):
        try:
            result = core.delete_profile(profile_id)
            return jsonify({
                "ok": True,
                "data": {"deleted": result}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/profiles/<int:profile_id>/activate", methods=["POST"])
    def activate_profile(profile_id):
        try:
            # Cek apakah profile exists
            profiles = core.get_profiles()
            profile_exists = any(p.id == profile_id for p in profiles)
            
            if not profile_exists:
                return jsonify({"ok": False, "error": "Profile not found"}), 404
            
            result = core.switch_profile(profile_id)
            
            return jsonify({
                "ok": True,
                "data": {"activated": result, "profile_id": profile_id}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    # =========================================================
    # SCHEDULE CRUD
    # =========================================================
    @app.route("/api/schedules")
    def get_schedules():
        try:
            profile_id = request.args.get("profile_id", type=int)
            
            if profile_id:
                schedules = core.get_schedules(profile_id)
            else:
                active_profile = core.get_active_profile()
                if not active_profile:
                    return jsonify({"ok": True, "data": []})
                schedules = core.get_schedules(active_profile.id)
            
            return jsonify({
                "ok": True,
                "data": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "bell_time": s.bell_time.strftime('%H:%M'),
                        "days": s.days_of_week,
                        "days_list": s.get_days_list(),
                        "audio_file": s.audio_file,
                        "is_active": s.is_active,
                        "profile_id": s.profile_id
                    }
                    for s in schedules
                ]
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/schedules", methods=["POST"])
    def create_schedule():
        try:
            data = request.get_json()

            profile_id = data.get("profile_id")
            if not profile_id:
                active_profile = core.get_active_profile()
                if not active_profile:
                    return jsonify({"ok": False, "error": "No active profile"}), 400
                profile_id = active_profile.id

            from datetime import time
            bell_time = time(
                int(data.get("hour", 0)),
                int(data.get("minute", 0))
            )

            days_list = data.get("days", [0,1,2,3,4,5])

            schedule_id = core.create_schedule(
                profile_id=profile_id,
                name=data.get("name"),
                bell_time=bell_time,
                days=days_list,
                audio_file=data.get("audio_file"),
                is_active=data.get("is_active", True)
            )

            return jsonify({
                "ok": True,
                "data": {"id": schedule_id}
            })

        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/schedules/<int:schedule_id>", methods=["PUT"])
    def update_schedule(schedule_id):
        try:
            data = request.get_json()
            
            from datetime import time
            update_data = {}
            
            if "name" in data:
                update_data["name"] = data["name"]
            if "hour" in data and "minute" in data:
                update_data["bell_time"] = time(data["hour"], data["minute"])
            if "days" in data:
                update_data["days_of_week"] = ",".join(map(str, data["days"]))
            if "audio_file" in data:
                update_data["audio_file"] = data["audio_file"]
            if "is_active" in data:
                update_data["is_active"] = data["is_active"]
            
            result = core.update_schedule(schedule_id, **update_data)
            
            return jsonify({
                "ok": True,
                "data": {"updated": result}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
    def delete_schedule(schedule_id):
        try:
            result = core.delete_schedule(schedule_id)
            return jsonify({
                "ok": True,
                "data": {"deleted": result}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route("/api/schedules/<int:schedule_id>/toggle", methods=["POST"])
    def toggle_schedule(schedule_id):
        try:
            schedule = core.get_schedule(schedule_id)
            if not schedule:
                return jsonify({"ok": False, "error": "Schedule not found"}), 404
            
            new_status = not schedule.is_active
            core.update_schedule(schedule_id, is_active=new_status)
            
            return jsonify({
                "ok": True,
                "data": {"is_active": new_status}
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    @app.route('/api/schedules/upload-audio', methods=['POST'])
    def upload_audio():
        try:
            if 'audio' not in request.files:
                return jsonify({"ok": False, "error": "No file provided"}), 400
            
            file = request.files['audio']
            if file.filename == '':
                return jsonify({"ok": False, "error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"ok": False, "error": "File type not allowed"}), 400
            
            # Buat folder jika belum ada
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Simpan file
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Handle duplicate filename
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{counter}{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                counter += 1
            
            file.save(filepath)
            relative_path = os.path.join("assets", "audio", filename)
            return jsonify({
                "ok": True,
                "data": {
                    "path": relative_path,
                    "filename": filename
                }
            })
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500
        
    # =========================================================
    # AUDIO FILES
    # =========================================================
    @app.route('/api/schedules/audio-files')
    def get_audio_files():
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            files = []

            for filename in os.listdir(UPLOAD_FOLDER):
                if allowed_file(filename):

                    relative_path = os.path.join(
                        "assets",
                        "audio",
                        filename
                    ).replace("\\", "/")

                    files.append({
                        "name": filename,
                        "path": relative_path
                    })

            files.sort(key=lambda x: x["name"])

            return jsonify({
                "ok": True,
                "data": files
            })

        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500
    # =========================================================
    # HISTORY
    # =========================================================
    @app.route("/api/history")
    def get_history():
        try:
            limit = request.args.get("limit", 100, type=int)
            history = core.get_history(limit)
            
            return jsonify({
                "ok": True,
                "data": [
                    {
                        "id": h.id,
                        "rang_at": h.rang_at.isoformat(),
                        "schedule_name": h.schedule_name,
                        "profile_name": h.profile_name,
                        "audio_played": h.audio_played,
                        "status": h.status
                    }
                    for h in history
                ]
            })
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

    # =========================================================
    # DAYS PRESET
    # =========================================================
    @app.route("/api/days-preset")
    def days_preset():
        return jsonify({
            "ok": True,
            "data": {
                "school_days": [0,1,2,3,4,5],
                "weekdays": [0,1,2,3,4],
                "weekend": [5,6],
                "all": [0,1,2,3,4,5,6],
                "labels": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            }
        })

    return app