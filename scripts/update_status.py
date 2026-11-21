"""Validate PROJECT_PLAN.md and refresh the generated README status views.

Usage:
    python scripts/update_status.py --validate
    python scripts/update_status.py --dry-run
    python scripts/update_status.py --write
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tracking.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
