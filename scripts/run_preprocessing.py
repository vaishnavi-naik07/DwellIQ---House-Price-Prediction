"""Run data preprocessing pipeline."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data_preprocessing import preprocess_data

if __name__ == "__main__":
    preprocess_data()

