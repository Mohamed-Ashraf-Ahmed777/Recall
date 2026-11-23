from pathlib import Path


TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log", ".py", ".c", ".cpp", ".java", ".html", ".css", ".js"}


def extract_text_from_file(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported text extension: {path.suffix}")
    return path.read_text(encoding="utf-8", errors="replace")
