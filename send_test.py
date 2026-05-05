#!/usr/bin/env python3
# send_test.py - Test IPC commands without GUI

import sys
import time

def main():
    from core.ipc_bus import get_ipc_bus
    
    if len(sys.argv) < 2:
        print("Usage: python send_test.py <command>")
        print("Commands: START_SCHEDULER, STOP_SCHEDULER, STATUS")
        sys.exit(1)
    
    command = sys.argv[1].upper()
    ipc = get_ipc_bus()
    
    if command == "START_SCHEDULER":
        print("Sending START_SCHEDULER...")
        ipc.send("START_SCHEDULER")
    elif command == "STOP_SCHEDULER":
        print("Sending STOP_SCHEDULER...")
        ipc.send("STOP_SCHEDULER")
    elif command == "STATUS":
        print("Sending STATUS...")
        ipc.send("STATUS")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    print("Command sent.")
    time.sleep(0.5)

if __name__ == "__main__":
    main()