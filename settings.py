import os
from dotenv import load_dotenv
load_dotenv()

PAYZE_API_KEY = os.environ.get("PAYZE_API_KEY")

DEBUG = os.environ.get("DEBUG") == "True"

QUIT_ON_ERROR = os.environ.get("QUIT_ON_ERROR") == "True"

LOGFILE_PATH = os.environ.get("LOGFILE_PATH")
DEBUGFILE_PATH = os.environ.get("DEBUGFILE_PATH")

BACKEND_URL = os.environ.get("BACKEND_URL").strip("/")

DJANGO_ADMIN_USERNAME = os.environ.get("DJANGO_ADMIN_USERNAME")
DJANGO_ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD")
