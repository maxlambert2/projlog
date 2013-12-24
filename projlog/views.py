from projlog import app
from forms import SignupForm,LoginForm
from flask import render_template, flash, redirect , Flask
from flask_login import LoginManager
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/index')
def index():
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('index.html', login_form=login_form, signup_form=signup_form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(user)
        return redirect('/index')
    return render_template('login.html', 
        title = 'Sign In',
        form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



def edit_profile():
    
    if request.method == 'POST':
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            conn = S3Connection('credentials', '')
            bucket = conn.create_bucket('bucketname')
            k = Key(bucket)
            k.key = 'foobar'
            k.set_contents_from_string(file.readlines())
            return "Success!"