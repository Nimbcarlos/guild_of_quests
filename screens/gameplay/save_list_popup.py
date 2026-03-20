from pathlib import Path

SAVE_FOLDER = Path("saves")

def list_saves():
    SAVE_FOLDER.mkdir(exist_ok=True)

    saves = []
    for file in SAVE_FOLDER.glob("*.json"):
        saves.append({
            "name": file.stem,
            "modified": file.stat().st_mtime
        })

    return sorted(saves, key=lambda x: x["modified"], reverse=True)