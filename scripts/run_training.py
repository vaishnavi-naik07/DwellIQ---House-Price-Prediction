"""Run model training pipeline."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.train_model import train_and_save_model

if __name__ == "__main__":
    train_and_save_model()

