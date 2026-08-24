import sys
from pathlib import Path

# Force the 'src' directory onto the path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ctl.main import Main

if __name__ == "__main__":
    Main()