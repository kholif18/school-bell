# core/ipc_bus.py
import sqlite3
import threading
import time
import json
import uuid
import logging
from core.paths import DB_PATH

logger = logging.getLogger(__name__)

class IPCBus:
    def __init__(self):
        self.running = False
        self.listener_thread = None
        self.handlers = {}

    def init_table(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ipc_commands (
            id TEXT PRIMARY KEY,
            command TEXT,
            payload TEXT,
            processed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()
        logger.info("IPC table initialized")

    def send(self, command, payload=None):
        """Send command from client to master"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ipc_commands (id, command, payload, processed) VALUES (?, ?, ?, 0)",
            (str(uuid.uuid4()), command, json.dumps(payload or {}))
        )
        conn.commit()
        conn.close()
        logger.info(f"IPC SEND => {command}")

    def register(self, command, callback):
        """Register handler for command (master only)"""
        self.handlers[command] = callback

    def start_listener(self):
        """Start listener thread with atomic command claiming (master only)"""
        if self.listener_thread:
            return

        self.running = True

        def worker():
            while self.running:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("BEGIN IMMEDIATE")  # ← LOCK DATABASE
                    
                    cur = conn.cursor()
                    # CLAIM ONE COMMAND AT A TIME
                    cur.execute(
                        "SELECT id, command, payload FROM ipc_commands WHERE processed = 0 ORDER BY created_at ASC LIMIT 1"
                    )
                    row = cur.fetchone()
                    
                    if row:
                        cmd_id, command, payload = row
                        payload = json.loads(payload or "{}")
                        
                        # CLAIM COMMAND IMMEDIATELY
                        cur.execute("UPDATE ipc_commands SET processed = 1 WHERE id = ?", (cmd_id,))
                        conn.commit()
                        
                        # RELEASE LOCK BEFORE HANDLER (prevent long lock)
                        conn.close()
                        
                        # EXECUTE HANDLER OUTSIDE TRANSACTION
                        logger.info(f"IPC RECEIVE => {command}")
                        if command in self.handlers:
                            try:
                                self.handlers[command](payload)
                            except Exception as e:
                                logger.error(f"IPC handler error {command}: {e}")
                    else:
                        conn.commit()
                        conn.close()
                    
                except sqlite3.OperationalError as e:
                    # Database locked - just retry
                    logger.debug(f"IPC listener DB locked, retrying: {e}")
                    if 'conn' in locals():
                        try:
                            conn.rollback()
                            conn.close()
                        except:
                            pass
                except Exception as e:
                    logger.error(f"IPC listener error: {e}")
                    if 'conn' in locals():
                        try:
                            conn.rollback()
                            conn.close()
                        except:
                            pass

                time.sleep(0.5)

        self.listener_thread = threading.Thread(target=worker, daemon=True)
        self.listener_thread.start()
        logger.info("IPC listener started with atomic command claiming")

    def stop_listener(self):
        self.running = False

_ipc_bus = None

def get_ipc_bus():
    global _ipc_bus
    if _ipc_bus is None:
        _ipc_bus = IPCBus()
    return _ipc_bus