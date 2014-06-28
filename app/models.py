from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from  app import db
import md5
from file_lib import get_s3_url
import config
import unicodedata
import re
from random import randrange


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
    db.Column('follower_id', Integer, ForeignKey('user.id')),  # @UndefinedVariable
    db.Column('followed_id', Integer, ForeignKey('user.id')),  # @UndefinedVariable
)
   

friends = db.Table('friends',   # @UndefinedVariable
    db.Column('user_id', Integer, ForeignKey('user.id')),  # @UndefinedVariable
    db.Column('friend_id', Integer, ForeignKey('user.id')),  # @UndefinedVariable
    created_date = Column(DateTime, default=datetime.datetime.now)
)

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    username = Column(String(30), unique=True)
    email = Column(String(60), unique=True)
    active = Column(Boolean, default=True)
    privacy = Column(SmallInteger, default=0)  #default privacy for projects: 0 is public; 1 is friends only; 2 is private projects
    pw_hash = Column(String(100))
    first_name = Column(String(30))
    last_name = Column(String(30))
    location = Column(String(30))
    profile_pic_id = Column(String(60))
    thumbnail_id = Column(String(60))
    follows = relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')
    friends = relationship('User',
        secondary = friends,
        primaryjoin = (friends.c.user_id==id),
        secondaryjoin = (friends.c.friend_id==id),
        lazy = 'dynamic'
        )
    
    projects = relationship('Project')

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.password = password
        self.pw_hash = generate_password_hash(password)
        
    def __repr__(self):
        return '<User %r>' % (self.username)
    
    def get_profile_url(self):
        return config.ROOT_URL + '/user/' + self.username
    
    def get_profile_pic_url(self):
        if self.profile_pic_id is None:
            return None
        else:
            file_name = self.profile_pic_id
            return get_s3_url(file_name)
    
    def get_thumbnail_url(self):
        file_name = self.thumbnail_id
        return get_s3_url(file_name)
    
    def get_full_name(self):
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
    id = Column(Integer, primary_key=True)
    id_str = Column(String(10))
    created_date = Column(DateTime, default=datetime.datetime.now)
    privacy_mode = Column(SmallInteger, default=0)
    created_by = Column(Integer, ForeignKey('user.id'))
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

    
    def get_id_str(self):
        id_str = str(base36encode(500000+ self.id *3 + randrange(1,3)))
        self.id_str=id_str
        return id_str
    
    def get_slug(self):
        if self.slug is None:
            name_sub = self.project_name[:config.SLUG_LENGTH]
            slug = unicodedata.normalize('NFKD', name_sub)
            slug = slug.encode('ascii', 'ignore').lower()
            slug = re.sub(r'[a-z0-9]+', '-', slug).strip('-')
            slug = re.sub(r'[-]+', '-', slug)
            self.slug=slug
        return self.slug
        
    def get_url(self):
        if self.slug is None or self.id_str is None:
            if self.slug is None:
                self.get_slug()
            if self.id_str is None:
                    self.get_id_str()
        path = '/project/'+str(self.id_str)+'/'+self.slug+'/'
        project_url = config.ROOT_URL+path
        return project_url
    
    def get_edit_url(self):
        edit_url = self.get_url()+'edit'
        return edit_url
    
    def get_pic_url(self):
        if self.pic_id is None:
            return None
        else:
            file_name = self.pic_id
            return get_s3_url(file_name)
    
    def get_thumbnail_url(self):
        file_name = self.thumbnail_id
        return get_s3_url(file_name)
    
class ProjectMember(db.Model):
    __tablename__ = 'project_member'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    member = Column(Integer, ForeignKey('user.id'))
    member_type = Column(SmallInteger)  #1: member; 2: advisor
    

class FollowRequest(db.Model):
    __tablename__ = 'follow_request'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    user_requesting = Column(Integer, ForeignKey('user.id'))
    user_approving = Column(Integer, ForeignKey('user.id'))
    approved = Column(Boolean, default=False)

class Post(db.Model):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    created_by =  Column(Integer, ForeignKey('user.id'))
    project = Column(Integer, ForeignKey('project.id'))
    text = Column(Text())
    pic_id = Column(String(100))
    comments = relationship('PostComment',  lazy='dynamic')
    likes = relationship('PostLike', lazy='dynamic')
    
    def get_pic_url(self):
        if self.pic_id is None:
            return None
        else:
            file_name = self.pic_id
            return get_s3_url(file_name)
    
class PostComment(db.Model):
    __tablename__ = 'post_comment'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    post = Column(Integer, ForeignKey('post.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    text = Column(Text())
    
class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = Column(Integer, primary_key=True)
    post = Column(Integer, ForeignKey('post.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    

    
    
       
    
    
    
    

    
    
    