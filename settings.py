import os
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
TESTING = DEBUG

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 9988))

APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(APP_FOLDER, "database.json")

try:
  from settings_local import *
except ImportError:
  pass