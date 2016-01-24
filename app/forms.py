from wtforms import TextField, TextAreaField, BooleanField, PasswordField, FileField, SelectField, IntegerField, ValidationError, HiddenField
from wtforms.validators import Required, Length, regexp
from models import User, Project
from flask_wtf import Form
import config
from app import db



class LoginForm(Form):
    username = TextField('Email/Username', validators = [Required()])
    password = PasswordField('Password', validators = [Required()])
    remember_me = BooleanField('Remember Me', default = False)
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if '@' in self.username.data:
            user = User.query.filter_by(email=self.username.data).first()  # @UndefinedVariable
        else:
            user = User.query.filter_by(username=self.username.data).first()# @UndefinedVariable
        
        if user is None:
            self.username.errors.append('Invalid Email or Password')
            return False
        elif user.is_locked():
            self.username.errors.append('Account is locked. Please try again in 2 minutes.')
            return False
        elif not user.check_password(self.password.data):
            self.username.errors.append('Invalid Email or Password')
            user.pass_tries_increment()
            db.session.add(user)# @UndefinedVariable
            db.session.commit()# @UndefinedVariable
            return False
        else:
            self.user = user
            return True
        
    
    
class SignupForm(Form):
    username = TextField('Username', validators = [Length(min=2, max=30),
        Required()])
    first_name = TextField('First Name', validators = [Length(min=2, max=40),
        Required()])
    email = TextField('Email', validators = [Length(min=6, max=40),
        Required()])
    password = PasswordField('Password', validators = [Length(min=6, max=20),
        Required()
    ])
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.username.data in config.INVALID_USERNAMES:
            self.username.errors.append( "Username already in use. Please pick another one")
            return False
        existing_email =  User.query.filter_by(email=self.email.data).first()  # @UndefinedVariable
        if existing_email is not None:
            self.email.errors.append( "Email already in use")
            return False
        existing_username = User.query.filter_by(username=self.username.data).first()  # @UndefinedVariable
        if existing_username is not None:
            self.username.errors.append( "Username already in use. Please pick another one")
            return False
        return True
            

    
class ProjectForm(Form):
    category = SelectField('Category', validators = [Required()],
                           choices =config.PROJECT_CATEGORIES)
    project_name = TextField('Title', validators = [Required(), Length(min=config.PROJ_NAME_MIN_LENGTH, max=config.PROJ_NAME_MAX_LENGTH)])
    goal = TextAreaField('Goal')
    privacy = SelectField('Privacy Setting', validators = [Required()], 
                                  choices=[('0', 'Public'), 
                                           ('1', 'ProjLog Friends Only'),
                                            ('2', 'Private (Project Members Only)')]
                                  )
    comments = TextAreaField('Comments')
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if hasattr(self,'created_by') and self.created_by is not None:
            user_id=self.created_by.id
            proj_name_exists = Project.query.filter_by(created_by_id=user_id,project_name=self.project_name.data).first()# @UndefinedVariable
            if proj_name_exists is not None:
                self.project_name.errors.append("Project Name already exists")
                return False
        return True
                

class PostForm(Form):
    user_id = IntegerField('user_id', validators = [Required()])  
    project_id = SelectField(u'Project', coerce=int)
    post_text = TextAreaField('',validators = [Required()])
    
class CommentForm(Form):
    user_id = IntegerField('user_id', validators = [Required()])  
    post_id = IntegerField('post_id', validators = [Required()])  
    comment_text = TextField('comment_text',validators = [Required()])
    
class FriendRequestForm(Form):
    requester_id = IntegerField('requester_id')
    requested_id = IntegerField('requested_id')

class FriendApproveForm(Form):
    requester_id = IntegerField('requester_id')
    requested_id = IntegerField('requested_id')
    approve = BooleanField('approve')

class ProfileForm(Form):
    username = TextField('Username', validators = [Required(), Length(min=2, max=40)])
    first_name = TextField('First Name or Nickname', validators = [Length(max=40)])
    last_name = TextField('Last Name', validators = [Length(max=40)])
    #profile_pic = FileField(u'Change Profile Picture', [regexp(u'^.*\.(jpg|JPG|png|PNG|jpeg|JPEG|gif|GIF)$')])
    location = TextField('Location', validators = [Length(max=40)])
    about = TextAreaField('About', validators=[Length(max=300)])
    privacy = SelectField('Profile Privacy', 
                                  choices=[('0', 'Public'), 
                                           ('1', 'Friends Only')], 
                                  validators = [Required()])
    gender = SelectField('Gender',
                         choices=[('', ""), ('f',"Female"), ('m', "Male")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.old_username = None
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.old_username is not None:
            if self.old_username == self.username.data:
                return True
            else: 
                user = User.query.filter_by(username=self.username.data).first()  # @UndefinedVariable
                if user is not None:
                    self.username.errors.append('username already taken')
                    return False
        return True
        
    
    
        
        
        
        
        
        
        
        