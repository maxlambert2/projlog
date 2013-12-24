from sqlalchemy import Column, Integer, String, ForeignKey
from projlog.database import Base
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    email = Column(String(60), unique=True)
    pw_hash = Column(String(100))
    full_name = Column(String(50))
    location = Column(String(50))
    picture_url = Column(String(100))
    project = relationship('Project', backref = 'creator', lazy = 'dynamic')

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.pw_hash = generate_password_hash(password)
        
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.username)
    
class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    creator = Column(Integer, ForeignKey('user.id'))
    project_name = Column(String(100))
    project_goal = Column(String(250))
    sponsor_1 = Column(Integer, ForeignKey('project.id'))
    sponsor_2 = Column(Integer, ForeignKey('project.id'))
    sponsor_3 = Column(Integer, ForeignKey('project.id'))
    
    
    