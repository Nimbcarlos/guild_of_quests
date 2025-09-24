from pathlib import Path
import os

# Resolução base (portrait)
BASE_WIDTH = 1024
BASE_HEIGHT = 800

# Caminho para a pasta de assets
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
BUTTONS_DIR = ASSETS_DIR / "buttons"
