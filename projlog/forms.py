from wtforms import Form, TextField, TextAreaField, BooleanField, PasswordField, FileField, validators
from wtforms.validators import Required, Length

class LoginForm(Form):
    username = TextField('Username', validators = [Required()])
    password =  password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    remember_me = BooleanField('remember_me', default = False)
    
    
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
    project_picture = FileField(u'Project Picture', [validators.regexp(u'^[^/\\]\.jpg$')])
    
class LogEntryForm(Form):
    comments = TextAreaField('Comments',validators = [Required()])
    picture = FileField(u'Picture', [validators.regexp(u'^[^/\\]\.jpg$')])

class ProfileForm(Form):
    first_name = TextField('First Name', validators = [Length(min=2, max=30)])
    last_name = TextField('First Name', validators = [Length(min=2, max=30)])
    profile_pic = FileField(u'Profile Picture', [validators.regexp(u'^[^/\\]\.jpg$')])
    company = TextField('Company', validators = [Length(min=2, max=40)])
    location = TextField('Location', validators = [Length(min=2, max=40)])