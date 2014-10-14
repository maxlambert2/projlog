from config.base import *
basedir = '/home/max/projlog/'

ROOT_URL="http://www.projlog.com"

AWS_S3_BUCKET = 'projlog'

S3_BUCKET_FOLDER = 'temp'

CSRF_ENABLED = True
SECRET_KEY  = os.environ.get("PROJLOG_SECRET_KEY")
DB_POSTGRES_PASS = os.environ.get("DB_POSTGRES_PASS")
SQLALCHEMY_DATABASE_URI = "postgresql://fochiller:"+DB_POSTGRES_PASS+"@localhost/projlog"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
ROOT_URL="http://www.projlog.com"
DEBUG_MODE = False
APP_ROOT='/home/max/projlog/app/'
UPLOAD_FOLDER = '/var/tmp/projlog.com/'
UPLOADS_DEFAULT_DEST=UPLOAD_FOLDER 
UPLOADS_FILES_DEST=UPLOAD_FOLDER 
