import os
from os.path import abspath, dirname

LOGO_URL = 'https://s3.amazonaws.com/projlog/projlog_logo.png'
#S3_BUCKET_URL = 'https://s3.amazonaws.com/projlog'

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
ALLOWED_PIC_FILE_EXT = u'^.*\.(jpg|JPG|png|PNG|jpeg|JPEG|gif|GIF)$'
PROJ_LIST_LIMIT=5
PROJ_NAME_MAX_LENGTH=50
PROJ_NAME_MIN_LENGTH=3
LARGE_PIC_DIM = (600,600)
THUMBNAIL_DIM=(50,50)
MEDIUM_PIC_DIM=(250,250)
SMALL_PIC_DIM=(100,100)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
DEFAULT_PROFILE_PIC = 'default_profile_pic.gif'
DEFAULT_PROFILE_PIC_MED = 'default_profile_pic_med.gif'

DEFAULT_THUMBNAIL = 'default_thumbnail.gif'
DEFAULT_IMG_EXT = 'PNG'
PROFILE_PIC_WIDTH=600

CSRF_ENABLED = True

AWS_S3_BUCKET = 'projlog'

S3_BUCKET_URL = 'https://s3.amazonaws.com/'+AWS_S3_BUCKET

SLUG_LENGTH=30

DEFAULT_IMG_SIZE='MEDIUM'

PROFILE_PIC_SIZES ={'large': LARGE_PIC_DIM, 
                   'medium': MEDIUM_PIC_DIM,
                   'thumbnail': THUMBNAIL_DIM}

POST_PIC_SIZES ={'large': LARGE_PIC_DIM, 
                   'medium': MEDIUM_PIC_DIM}

PROJ_PIC_SIZES = {'large':LARGE_PIC_DIM,
                  'medium': MEDIUM_PIC_DIM,
                  'thumbnail':THUMBNAIL_DIM }


DEFAULT_PIC_SIZE = 'medium'
