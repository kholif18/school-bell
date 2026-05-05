# bootstrap/app_launcher.py
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="School Bell Automation System",
        epilog="Examples:\n"
               "  python main.py           # Run GUI mode\n"
               "  python main.py --headless # Run background service\n"
               "  python main.py --tray    # Run system tray mode"
    )
    parser.add_argument('--headless', action='store_true', help='Run as background service (no GUI)')
    parser.add_argument('--tray', action='store_true', help='Run as system tray application')
    parser.add_argument('--version', action='store_true', help='Show version')
    return parser.parse_args()

def launch():
    args = parse_args()
    
    if args.version:
        try:
            from core.config_manager import get_config
            config = get_config()
            print(f"School Bell Automation System v{config.get('version', '1.0.0')}")
        except:
            print("School Bell Automation System v1.0.0")
        return
    
    if args.headless:
        # Lazy import - only when needed
        from bootstrap.service_runner import run_service
        run_service()
    elif args.tray:
        # Lazy import - only when needed  
        from bootstrap.tray_runner import run_tray
        run_tray()
    else:
        # Lazy import - only when needed
        from bootstrap.gui_runner import run_gui
        run_gui()

if __name__ == "__main__":
    launch()