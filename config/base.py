import os
from os.path import abspath, dirname

LOGO_URL = 'https://s3.amazonaws.com/projlog/projlog_logo.png'
#S3_BUCKET_URL = 'https://s3.amazonaws.com/projlog'

ALLOWED_PIC_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
ALLOWED_PIC_FILE_EXT = u'^.*\.(jpg|JPG|png|PNG|jpeg|JPEG|gif|GIF)$'
PROJ_LIST_LIMIT=5
PROJ_NAME_MAX_LENGTH=50
PROJ_NAME_MIN_LENGTH=3

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
DEFAULT_PROFILE_PIC = 'default_profile_pic.gif'
DEFAULT_PROFILE_PIC_MED = 'default_profile_pic_med.gif'

DEFAULT_THUMBNAIL = 'default_thumbnail.gif'
DEFAULT_IMG_EXT = 'jpg'
PROFILE_PIC_WIDTH=600

CSRF_ENABLED = True
AWS_S3_BUCKET = 'projlog'
S3_BUCKET_URL = 'https://s3.amazonaws.com/'+AWS_S3_BUCKET
SLUG_LENGTH=30

LARGE_PIC_DIM = (640,480)
THUMBNAIL_DIM=(35,35)
MEDIUM_PIC_DIM=(250,250)
SMALL_PIC_DIM = (100, 100)
TINY_PIC_DIM = (70,70)
DEFAULT_IMG_SIZE='large'
DEFAULT_PROFILE_PIC_SIZE='medium'
COVER_PIC_DIM = (700,200)

PROFILE_PIC_SIZES ={'medium': MEDIUM_PIC_DIM,
                    'thumbnail':THUMBNAIL_DIM,
                   'small': SMALL_PIC_DIM,
                   'tiny': TINY_PIC_DIM
                   }

POST_PIC_SIZES ={'large': LARGE_PIC_DIM,
                 'small' : SMALL_PIC_DIM }

PROJ_PIC_SIZES = {'large':COVER_PIC_DIM,
                  'small':SMALL_PIC_DIM,
                  'medium':MEDIUM_PIC_DIM,
                  'thumbnail': THUMBNAIL_DIM }


DEFAULT_PIC_SIZE = 'medium'

POST_TYPE =dict(create_project=2,
               default=0)        
            
PROJECT_CATEGORIES = [ 
                       ('food', 'Food'),
                      ('vis_art', 'Visual Arts'),
                    ('sport', 'Fitness/Sports'),
                    ('tech', 'Technology'),
                    ('science', 'Science'),
                    ('craft', 'Crafts/DIY'),
                    ('fashion', 'Fashion'),
                    ('music', 'Music'),
                    ('publishing', 'Publishing/Books'),
                    ('travel', 'Travel')
                    ]       

PROJECT_CATEGORIES.sort(key=lambda tup: tup[1]) 

INVALID_USERNAMES = ['user', 'login', 'post', 'logout', 'login', 'index', 'signup', 'projlog'
                      'my_friends', 'unfollow', 'follow', 'project', 'create_project', 'post_comment',
                      'ajax_post', 'friend_requests', 'approve_friend', 'edit_profile' ,]
