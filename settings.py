import os
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL").strip("/")

DJANGO_ADMIN_USERNAME = os.environ.get("DJANGO_ADMIN_USERNAME")
DJANGO_ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD")
