from pathlib import Path

def load_stylesheet(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Style not found: {file_path}")

    return path.read_text(encoding="utf-8")