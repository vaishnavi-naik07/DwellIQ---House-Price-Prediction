"""Run exploratory data analysis."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.eda import run_comprehensive_eda

if __name__ == "__main__":
    run_comprehensive_eda()

