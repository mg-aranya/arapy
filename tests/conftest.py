import sys
from pathlib import Path

# Ensure the project root (which contains the 'arapy' package directory)
# is on sys.path so tests can import 'arapy.*' without an installed package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

