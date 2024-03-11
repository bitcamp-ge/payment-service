import os
from dotenv import load_dotenv
load_dotenv()

LOGFILE_PATH = os.environ.get("LOGFILE_PATH")
DEBUGFILE_PATH = os.environ.get("DEBUGFILE_PATH")

BACKEND_URL = os.environ.get("BACKEND_URL").strip("/")

DJANGO_ADMIN_USERNAME = os.environ.get("DJANGO_ADMIN_USERNAME")
DJANGO_ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD")
