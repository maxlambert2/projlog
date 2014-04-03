import os
from os.path import abspath, dirname

LOGO_URL = 'https://s3.amazonaws.com/projlog/projlog_logo.png'
S3_BUCKET_URL = 'https://s3.amazonaws.com/projlog'

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
PROJ_LIST_LIMIT=5
PROJ_NAME_MAX_LENGTH=50
PROJ_NAME_MIN_LENGTH=3
PROFILE_PIC_WIDTH=150
PROFILE_PIC_HEIGHT=150
THUMBNAIL_SIZE=40
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = 'projlog'
DEFAULT_PROFILE_PIC_URL= '/static/default_profile_pic.jpeg'
DEFAULT_IMG_EXT = '.jpg'

CSRF_ENABLED = True
