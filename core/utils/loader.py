from core.utils.resource import resource_path

def load_stylesheet(filename):
    path = resource_path(f"apps/desktop/styles/{filename}")

    if not path.exists():
        raise FileNotFoundError(f"Style not found: {path}")

    return path.read_text(encoding="utf-8")