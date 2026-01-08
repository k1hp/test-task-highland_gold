import pathlib
from logging import Logger

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "task" / "database"
LOGGER = Logger("general logger")