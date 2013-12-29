from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
#from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from database import Base
#import string
#import random


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    username = Column(String(30), unique=True)
    email = Column(String(60), unique=True)
    active = Column(Boolean, default=True)
    pw_hash = Column(String(100))
    full_name = Column(String(50))
    location = Column(String(50))
    picture_id = Column(String(100))
    is_private = Column(Boolean, default=False)

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.pw_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
        
    def set_full_name(self, full_name):
        self.full_name = full_name
    
    def set_location(self,location):
        self.location = location
        
    def set_picture(self,pic_url):
        self.picture_url=pic_url
        
    def deactivate(self):
        self.active = False
    
    def reactivate(self):
        self.active = True  

    def is_active(self):
        return self.active

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)
    
class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(Integer, ForeignKey('user.id'))
    project_name = Column(String(40))
    project_goal = Column(String(100))
    background_pic_id = Column(String(100))
    thumbnail_id = Column(String(100))
    comments = Column(Text())

class FollowRequests(Base):
    __tablename__ = 'follow_requests'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    user_requesting = Column(Integer, ForeignKey('user.id'))
    user_approving = Column(Integer, ForeignKey('user.id'))
    approved = Column(Boolean, default=False)

class LogEntry(Base):
    __tablename__ = 'log_entry'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    project = Column(Integer, ForeignKey('project.id'))
    text = Column(Text())
    picture_url = Column(String(100))
    
class ProjectComment(Base):
    __tablename__ = 'project_comment'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    project = Column(Integer, ForeignKey('project.id'))
    text = Column(Text())
    
class LogEntryComment(Base):
    __tablename__ = 'log_entry_comment'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    log_entry = Column(Integer, ForeignKey('log_entry.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    text = Column(Text())
    
class LogEntryLike(Base):
    __tablename__ = 'log_entry_like'
    id = Column(Integer, primary_key=True)
    log_entry = Column(Integer, ForeignKey('log_entry.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    
class UserFollow(Base):
    __tablename__ = 'user_follow'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'))
    follower = Column(Integer, ForeignKey('user.id'))
    
class ProjectFollow(Base):
    __tablename__ = 'project_follow'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    project_id = Column(Integer, ForeignKey('project.id'))
    follower = Column(Integer, ForeignKey('user.id'))
    
    
       
    
    
    
    

    
    
    