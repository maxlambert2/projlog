#from projlog import app
from forms import SignupForm,LoginForm
from flask import render_template, flash, redirect , Flask, url_for, request, g, session
from flask_login import login_user, logout_user, login_required
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug.utils import secure_filename
from projlog.models import User
from projlog.database import db_session
from projlog import login_manager

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

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User,int(user_id))  # @UndefinedVariable

@app.route('/login', methods = ['POST'])
def login():
    if g.user is not None and g.user.is_active():
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
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
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