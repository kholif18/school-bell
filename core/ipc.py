# core/ipc.py
import sqlite3
import json
import uuid
import threading
import time
import logging
from typing import Callable, Dict, Any, Optional

from core.paths import DB_PATH

logger = logging.getLogger(__name__)


class IPCBus:
    """
    Lightweight IPC layer (optional multi-process support)

    Design:
    - SQLite queue (simple, no Redis / no socket complexity)
    - Fire-and-forget command model
    - Single listener thread (master process only)
    """

    def __init__(self):
        self._handlers: Dict[str, Callable[[dict], None]] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # =========================
    # INIT
    # =========================

    def init(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ipc_queue (
            id TEXT PRIMARY KEY,
            command TEXT,
            payload TEXT,
            processed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    # =========================
    # SEND (CLIENT → MASTER)
    # =========================

    def send(self, command: str, payload: dict = None):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO ipc_queue (id, command, payload, processed) VALUES (?, ?, ?, 0)",
            (str(uuid.uuid4()), command, json.dumps(payload or {}))
        )

        conn.commit()
        conn.close()

    # =========================
    # REGISTER HANDLER
    # =========================

    def on(self, command: str, handler: Callable[[dict], None]):
        self._handlers[command] = handler

    # =========================
    # LISTENER LOOP
    # =========================

    def start_listener(self):
        if self._thread:
            return

        self._running = True

        def loop():
            while self._running:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("BEGIN IMMEDIATE")

                    cur = conn.cursor()
                    cur.execute("""
                        SELECT id, command, payload
                        FROM ipc_queue
                        WHERE processed = 0
                        ORDER BY created_at ASC
                        LIMIT 1
                    """)

                    row = cur.fetchone()

                    if row:
                        cmd_id, command, payload = row
                        data = json.loads(payload or "{}")

                        cur.execute(
                            "UPDATE ipc_queue SET processed = 1 WHERE id = ?",
                            (cmd_id,)
                        )

                        conn.commit()
                        conn.close()

                        handler = self._handlers.get(command)
                        if handler:
                            try:
                                handler(data)
                            except Exception as e:
                                logger.error(f"IPC handler error {command}: {e}")

                    else:
                        conn.commit()
                        conn.close()

                except Exception as e:
                    logger.error(f"IPC loop error: {e}")
                    time.sleep(1)
                    try:
                        conn.close()
                    except:
                        pass

                time.sleep(0.3)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        logger.info("IPC listener started")

    # =========================
    # STOP
    # =========================

    def stop(self):
        self._running = False


# singleton
_ipc = None
_lock = threading.Lock()


def get_ipc():
    global _ipc
    with _lock:
        if _ipc is None:
            _ipc = IPCBus()
            _ipc.init()
        return _ipc