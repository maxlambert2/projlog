import os
from unipath import Path

CSRF_ENABLED = True
SECRET_KEY  = os.environ.get("PROJLOG_SECRET_KEY")