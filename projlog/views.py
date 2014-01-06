from projlog import app, login_manager
from forms import SignupForm, LoginForm, ProfileForm
from flask import render_template, flash, redirect , Flask, url_for, request, g, session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from werkzeug.utils import secure_filename
from projlog.models import User
from projlog import database

db_session = database.Session()

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
    if request.method == 'POST' and form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('login.html', 
        title = 'Login',
        form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(form.username.data, form.email.data,
                form.password.data)
        flash('Creating account')
        db_session.add(user)
        return redirect(url_for('update_profile'))
    return render_template('signup.html', signup_form=form, email = form.email)


@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = ProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = load_user(current_user.id)
        user.location = form.location
        user.first_name = form.first_name
        user.last_name = form.last_name
        try:
            db_session.commit()  # @UndefinedVariable
        except:
            db_session.rollback()
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