from io import TextIOWrapper
from pathlib import Path

TIMEOUT_PER_PAGE: int | None = None
MAX_WORKERS: int | None = None
SAVE_TRACE: bool | None = None
HEADLESS: bool | None = None
SKIP_EDGE: bool | None = None

URLS_INPUT: TextIOWrapper | None = None
ARIA2_OUTPUT: Path | None = None
