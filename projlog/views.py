from projlog import app
from forms import SignupForm, LoginForm, ProfileForm
from flask import render_template, flash, redirect , Flask, url_for, request, g, session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug.utils import secure_filename
from projlog.models import User
from projlog.database import db_session

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
@app.route('/index')
def index():
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('index.html', login_form=login_form, signup_form=signup_form)

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User,int(user_id))  # @UndefinedVariable


@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user is not None and current_user.is_active():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for("index"))
    error = form.user.username.error
    return render_template('login.html', 
        title = 'Login',
        form = form,
        error_msg = error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)  # @UndefinedVariable
        db_session.commit()  # @UndefinedVariable
        flash('Creating account')
        return redirect(url_for('update_profile'))
    return render_template('signup.html', form=form)


@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = ProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        current_user.location = form.location
        current_user.full_name = form.full_name
        db_session.commit()  # @UndefinedVariable
        return url_for("index")
    return render_template('update_profile.html', form=form)
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have logged out')
    return redirect(url_for("index"))




# 
# 
# 
# def edit_profile():
#     
#     if request.method == 'POST':
#         file = request.files['profile_pic']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             conn = S3Connection('credentials', '')
#             bucket = conn.create_bucket('bucketname')
#             k = Key(bucket)
#             k.key = 'foobar'
#             k.set_contents_from_string(file.readlines())
#             return "Success!"