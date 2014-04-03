from wtforms import TextField, TextAreaField, BooleanField, PasswordField, FileField, SelectField, validators, ValidationError
from wtforms.validators import Required, Length
from models import User
from flask_wtf import Form
import config



class LoginForm(Form):
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    remember_me = BooleanField('Remember Me', default = False)
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        user = User.query.filter_by(email=self.email.data).first()  # @UndefinedVariable
        if user is None:
            self.email.errors.append('Invalid Email or Password')
            return False
        self.user = user
        return True
        
    
    
class SignupForm(Form):
    username = TextField('username', [validators.Length(min=2, max=30)])
    email = TextField('Email', [validators.Length(min=6, max=40)])
    password = PasswordField('Password', [
        validators.Required()
    ])
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        existing_email =  User.query.filter_by(email=self.email.data).first()  # @UndefinedVariable
        if existing_email is not None:
            self.email.errors.append( "Email already in use")
            return False
        existing_username = User.query.filter_by(username=self.username.data).first()  # @UndefinedVariable
        if existing_username is not None:
            self.username.errors.append( "Username already in use")
            return False
        return True
            
         
    
class ProjectCreateForm(Form):
    project_name = TextField('Project Name*', validators = [Required(), Length(min=config.PROJ_NAME_MIN_LENGTH, max=config.PROJ_NAME_MAX_LENGTH)])
    goal = TextField('Goal*', validators = [Required(), Length(min=6, max=150)])
    privacy = SelectField('Privacy Setting*', 
                                  choices=[('0', 'Public'), 
                                           ('1', 'Friends Only'),
                                           ('2', 'Private (Project Members & Advisors Only)')],
                                  validators = Required())
    comments = TextField('Comments')
    
class ProjectEditForm(Form):
    name = TextField('Project Name', validators = [Required(), Length(min=config.PROJ_NAME_MIN_LENGTH, max=config.PROJ_NAME_MAX_LENGTH)])
    goal = TextField('Project Goal', validators = [Required(), Length(min=6, max=150)])
    comments = TextAreaField('Comments')
    privacy = SelectField('Privacy Setting*', 
                                  choices=[('0', 'Public'), 
                                           ('1', 'Friends Only')], 
                                  validators = Required())
    picture = FileField(u'Project Picture', [validators.regexp(u'^.*\.(jpg|JPG)$')])
    
    
class LogEntryForm(Form):
    comments = TextAreaField('Comments',validators = [Required()])
    picture = FileField(u'Picture', [validators.regexp(u'^.*\.(jpg|JPG)$')])

class ProfileForm(Form):
    username = TextField('Username', validators = [Required(), Length(min=2, max=40)])
    first_name = TextField('First Name', validators = [Length(max=40)])
    last_name = TextField('Last Name', validators = [Length(max=40)])
    #profile_pic = FileField(u'Profile Picture', [validators.regexp(u'^.*\.(jpg|JPG|png|PNG)$')])
    location = TextField('Location', validators = [Length(max=40)])

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
        
    
    
        
        
        
        
        
        
        
        