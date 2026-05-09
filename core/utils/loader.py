from core.utils.resource import resource_path


def load_stylesheet(filename):

    file_path = resource_path(
        f"apps/desktop/styles/{filename}"
    )

    print("STYLE PATH:", file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Style not found: {file_path}"
        )

    return file_path.read_text(encoding="utf-8")