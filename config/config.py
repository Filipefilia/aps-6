from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATASET_DIR = PROJECT_DIR / 'dataset'

# Define o nível de acesso mínimo necessário para garantir o acesso.
REQUIRED_ACCESS_LEVEL = "2"