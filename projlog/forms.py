from wtforms import Form, TextField, TextAreaField, BooleanField, PasswordField, FileField, validators
from wtforms.validators import Required, Length
from models import User

class LoginForm(Form):
    username = TextField('Username or Email', [validators.Required()])
    password =  password = PasswordField('Password', [validators.Required()])
    remember_me = BooleanField('remember_me', default = False)
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        self.username.errors = None
        if self.username.find('@') != -1:  #email given
            user = User.query.filter_by(email=self.username.data).first()  # @UndefinedVariable
            if user is None:
                self.username.errors.append('Invalid Username/Password')
                return False
            
        else:
            user = User.query.filter_by(username=self.username.data).first()  # @UndefinedVariable
            if user is None:
                self.username.errors.append('Invalid Username/Password')
                return False
        self.user=user
        return True
        
    
    
class SignupForm(Form):
    username = TextField('Username', [validators.Length(min=3, max=25)])
    email = TextField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    
class ProjectCreateForm(Form):
    project_name = TextField('Project Name', validators = [Required(), Length(min=6, max=60)])
    project_goal = TextField('Project Goal')
    project_comments = TextAreaField('Comments')
    project_picture = FileField(u'Project Picture', [validators.regexp(u'^.*\.(jpg|JPG)$')])
    
class LogEntryForm(Form):
    comments = TextAreaField('Comments',validators = [Required()])
    picture = FileField(u'Picture', [validators.regexp(u'^.*\.(jpg|JPG)$')])

class ProfileForm(Form):
    full_name = TextField('Full Name', validators = [Length(min=2, max=30)])
    profile_pic = FileField(u'Profile Picture', [validators.regexp(u'^.*\.(jpg|JPG)$')])
    location = TextField('Location', validators = [Length(min=2, max=40)])
    
    
        
        
        
        
        
        
        
        