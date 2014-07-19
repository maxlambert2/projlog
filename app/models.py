from sqlalchemy.orm import relationship, backref
from sqlalchemy import MetaData, Column, String, Boolean, Text, Integer, DateTime, SmallInteger, ForeignKey, Sequence
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from  app import db
import md5
from file_lib import get_s3_url, generate_filename, resize_and_crop
import config
import unicodedata
import re
from random import randrange
import boto
from datetime import datetime, timedelta

#import string
#import random

def base36encode(number):
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')

    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]

metadata = MetaData()

followers = db.Table('followers',  # @UndefinedVariable
    db.Column('follower_id', Integer, ForeignKey('user.id'), index=True),  # @UndefinedVariable
    db.Column('followed_id', Integer, ForeignKey('user.id'), index=True),  # @UndefinedVariable
)
   

friendships = db.Table('friendships',   # @UndefinedVariable
    db.Column('user_id', Integer, ForeignKey('user.id'), index=True),  # @UndefinedVariable
    db.Column('friend_id', Integer, ForeignKey('user.id')),  # @UndefinedVariable
    created_date = Column(DateTime, default=datetime.now)
)

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    username = Column(String(30), unique=True)
    email = Column(String(60), unique=True)
    active = Column(Boolean, default=True)
    privacy = Column(Integer, default=0)  #default privacy for projects: 0 is public; 1 is friends only; 2 is private projects
    pw_hash = Column(String(100))
    first_name = Column(String(30))
    last_name = Column(String(30))
    location = Column(String(30))
    gender = Column(String(1))
    profile_pic_id = Column(String(60))
    about = Column(Text)
    follows = relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')
    friends = relationship('User',
        secondary = friendships,
        primaryjoin = (friendships.c.user_id==id),
        secondaryjoin = (friendships.c.friend_id==id),
        backref = backref('friendships', lazy = 'dynamic'),
        lazy='dynamic'
        )

    
    projects = relationship('Project', backref='created_by')
    

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.password = password
        self.pw_hash = generate_password_hash(password)
        self.privacy=0
       
        
    def __repr__(self):
        return '<User %r>' % (self.username)
    
    def is_private(self):
        return self.privacy == 1;
    
    def get_privacy(self):
        if self.privacy is None:
            return 0;
        else:
            return self.privacy

    def get_location(self):
        if self.location is None:
            return ''
        else:
            return self.location
    
    def has_notifications(self):
        return Notification.query.filter_by(user_id=self.id,seen=False).count() > 0
    
    def notification_count(self):
        return Notification.query.filter_by(user_id=self.id,seen=False).count()
        
    def get_notifications(self):
        return Notification.query.filter_by(user_id=self.id, seen=False).limit(10).all()
    
    def is_viewable_by(self,user_id):
        if self.is_private == False or self.id == user_id:
            return True
        elif self.friends.filter(friendships.c.user_id == user_id).count() > 0:
            return True
        else:
            return False
    
    def get_profile_url(self):
        return config.ROOT_URL + '/user/' + self.username
    
    def get_profile_pic_filename(self, file_ext=config.DEFAULT_IMG_EXT):
        if self.profile_pic_id is None:
            self.profile_pic_id = generate_filename(self.username, ext=file_ext)
        return self.profile_pic_id
                
    def get_profile_pic_url(self,size='large'):
        if self.profile_pic_id is None:
            file_name = config.DEFAULT_PROFILE_PIC
        else:
            file_name = size+'/'+self.profile_pic_id
        return get_s3_url(file_name)

    def get_thumbnail_url(self):
        if not self.profile_pic_id:
            return get_s3_url(config.DEFAULT_THUMBNAIL)
        else:
            return self.get_profile_pic_url(size='thumbnail')
    
    def get_profile_pic_medium_url(self):
        if not self.profile_pic_id:
            return get_s3_url(config.DEFAULT_PROFILE_PIC_MED)
        else:
            return self.get_profile_pic_url(size='medium')
    
    def get_profile_pic_large_url(self):
        return self.get_profile_pic_url(size='large')
    
    def set_profile_pic(self, filepath, file_ext=config.DEFAULT_IMG_EXT):
        conn = boto.connect_s3(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
        bucket=conn.get_bucket(config.AWS_S3_BUCKET)
        profile_pic_id = self.get_profile_pic_id(file_ext=file_ext)
        for size, dim in config.PROFILE_PIC_SIZES.iteritems():  
            pic = resize_and_crop(filepath, dim)
            pic_id = size.lower()+'-'+profile_pic_id
            key_pic = bucket.new_key(pic_id)
            key_pic.set_contents_from_file(pic)  
            key_pic.set_acl('public-read')
        
        
    def get_full_name(self):
        if self.first_name is None:
            return self.username
        else:
            return self.first_name + ' ' + self.last_name
         
    def is_authenticated(self):
        return True
        
    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
        
    def set_full_name(self, full_name):
        self.full_name = full_name
    
    def set_location(self,location):
        self.location = location
    
    def set_private(self):
        self.is_private = True
        
    def set_public(self):
        self.is_private = False
        
    def set_picture_id(self):
        pic_id = md5.new(self.email).digest()
        self.profile_pic_id=pic_id
        return pic_id
        
    def deactivate(self):
        self.active = False
    
    def reactivate(self):
        self.active = True  

    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def posts_followed(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.created_by)).filter(followers.c.follower_id == self.id).order_by(Post.created_date.desc())

    def update_profile(self, username, first_name, last_name, location, profile_pic_url):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.location = location
        self.profile_pic_url = profile_pic_url
        
#         if pic and allowed_file(pic.filename):
#                 filename = secure_filename(pic.filename)
#                 profile_pic = resize_image(filename, width=config.PROFILE_PIC_WIDTH)
#                 thumbnail = resize_image(pic, width=config.THUMBNAIL_SIZE)
#                 AK = config.AWS_ACCESS_KEY_ID
#                 SK = config.AWS_SECRET_ACCESS_KEY
#                 conn = boto.connect_s3()
#                 b=conn.get_bucket(config.AWS_S3_BUCKET)
#                 k=b.new_key()
#                 k.key = username+'-profile_pic.png'
#                 k.set_contents_from_string(profile_pic.getvalue())              
        try:
            db.session.add(self)  # @UndefinedVariable
            db.session.commit()  # @UndefinedVariable
        except:
            db.session.rollback()  # @UndefinedVariable
            return False
        return True


class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, Sequence('proj_id_seq', start=20000), primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    privacy_mode = Column(SmallInteger, default=0)
    created_by_id = Column(Integer, ForeignKey('user.id'), index=True)
    project_name = Column(String(50))
    goal = Column(String(200))
    slug = Column(String(30))
    comments=Column(Text)
    pic_id = Column(String(100))
    thumbnail_id = Column(String(100))
    description = Column(Text)
    posts = relationship('Post',  lazy = 'dynamic')
    members = relationship('ProjectMember')
    
    def __init__(self, project_name, goal, created_by, privacy):
        self.project_name=project_name
        self.goal=goal
        self.created_by = created_by
        self.privacy_mode=privacy

    def has_pic(self):
        if self.pic_id is None:
            return False
        else:
            return True
    
    def is_viewable_by(self, user_id):
        return True
    
    def get_slug(self):
        _slugify_strip_re = re.compile(r'[^\w\s-]')
        _slugify_hyphenate_re = re.compile(r'[-\s]+')
        value = self.project_name[:config.SLUG_LENGTH]
        if not isinstance(value, unicode):
            value = unicode(value)
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(_slugify_strip_re.sub('', value).strip().lower())
        slug = _slugify_hyphenate_re.sub('-', value)
        self.slug=slug
        return self.slug
        
    def get_url(self):
        updated=0
        if self.slug is None or len(self.slug.strip())==0:
            self.get_slug()
            updated+=1
        path = '/project/'+str(self.id)+'/'+self.slug
        project_url = config.ROOT_URL+path
        if updated > 0:
            try:
                db.session.add(self)  # @UndefinedVariable
                db.session.commit()  # @UndefinedVariable
            except:
                db.session.rollback()  # @UndefinedVariable
        return project_url
    
    def get_edit_url(self):
        edit_url = self.get_url()+'/edit'
        return edit_url
    
    def get_pic_url(self,size=config.DEFAULT_PIC_SIZE):
        if self.pic_id is None:
            return None
        else:
            path = size+'/'+self.pic_id
            return get_s3_url(path)
    
    def get_pic_thumbnail_url(self):
        return self.get_pic_url('thumbnail')
    
class ProjectMember(db.Model):
    __tablename__ = 'project_member'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), index=True)
    member = Column(Integer, ForeignKey('user.id'))
    

class Notification(db.Model):
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    user_id =  Column(Integer, ForeignKey('user.id'), index=True)
    message = Column(String(100))
    link = Column(String(100))
    seen = Column(Boolean, default=False)
        
    def __init__(self, user_id, message, link):
        self.message=message
        self.user_id=user_id
        self.link=link
        
    def get_link(self):
        return self.link+"?nid="+str(self.id)
        
class NotificationMixin(object):
    def __init__(self,user_id, msg, link):
        notif = Notification(user_id=user_id, message =msg,link=link)
        db.session.add(notif)  # @UndefinedVariable


class FriendRequest(NotificationMixin, db.Model):
    __tablename__ = 'friend_request'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    requester_id = Column(Integer, ForeignKey('user.id'))
    requested_id = Column(Integer, ForeignKey('user.id'), index=True)
    approved = Column(Boolean, default=False)
    ignored = Column(Boolean, default=False)
    requester = relationship('User', foreign_keys=[requester_id])
                            

    def __init__(self,requester_user_id, requested_user_id):
        requester = User.query.get(requester_user_id)
        msg = requester.get_full_name()+" sent you a friend request"
        link = "/friend_requests"
        super(FriendRequest,self).__init__(user_id=requested_user_id, msg=msg,link=link)
        self.requester_id = requester_user_id
        self.requested_id = requested_user_id
            
class Post(db.Model):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    created_by =  Column(Integer, ForeignKey('user.id'))
    project = Column(Integer, ForeignKey('project.id'), index=True)
    text = Column(Text())
    pic_id = Column(String(50))
    comments = relationship('PostComment',  lazy='dynamic')
    likes = relationship('PostLike', lazy='dynamic')
    
    def get_pic_url(self,size='large'):
        if self.pic_id is None:
            return None
        path = size+self.pic_id
        return get_s3_url(path)
    
    def get_created_date_str(self):
        diff = datetime.now()-self.created_date
        if diff.days > 10:
            return self.created_date.strftime("%B %d, %Y")
        if diff.days > 1:
            return str(diff.days)+' days ago'
        elif diff.hours > 1:
            return str(diff.hours)+ ' hours ago'
        else:
            return str(diff.minutes)+ ' minutes ago'
            
    
class PostComment(NotificationMixin, db.Model):
    __tablename__ = 'post_comment'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    post = Column(Integer, ForeignKey('post.id'), index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    text = Column(Text())
    
    def __init__(self,user_id,user_name, post_id,text, link):
        msg = user_name+" commented on your post"
        super(PostComment,self).__init__(user_id=user_id, msg=msg,link=link)
        self.user_id=user_id
        self.post=post_id
        self.text=text
    
class PostLike(NotificationMixin,  db.Model):
    __tablename__ = 'post_like'
    id = Column(Integer, primary_key=True)
    post = Column(Integer, ForeignKey('post.id'), index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    
    def __init__(self,user_id,user_name, post_id, link):
        msg = user_name+" liked your post"
        super(PostLike,self).__init__(user_id=user_id, msg=msg,link=link)
        self.user_id=user_id
        self.post=post_id

    
    
       
    
    
    
    

    
    
    