from app import app, db, login_manager
from forms import SignupForm, LoginForm, ProfileForm, ProjectCreateForm
from flask import render_template, flash, redirect , Flask, url_for, request, g, session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from models import User, Project
import config
from file_manager import resize_image, allowed_file
import time, base64, urllib, json, hmac
from hashlib import sha1


def get_s3_url(object_name):
    return 'https://s3.amazonaws.com/%s/%s' % (config.AWS_S3_BUCKET, object_name)

@app.route('/sign_s3_upload/')
def sign_s3():

    object_name = request.args.get('s3_object_name')
    mime_type = request.args.get('s3_object_type')

    expires = int(time.time()+10)
    amz_headers = "x-amz-acl:public-read"

    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, config.AWS_S3_BUCKET, object_name)

    signature = base64.encodestring(hmac.new(config.AWS_SECRET_ACCESS_KEY, put_request, sha1).digest())
    signature = urllib.quote_plus(signature.strip())

    url = get_s3_url(object_name)

    return json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, config.AWS_ACCESS_KEY_ID, expires, signature),
         'url': url
      })
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)  # @UndefinedVariable

@app.before_request
def before_request():
    g.user=None
    if current_user.is_authenticated():
        g.user = current_user
    
@app.route('/')
def index():
    if current_user is None or not current_user.is_active():
        return landing_page()
    posts = current_user.posts_followed()
    user_projects = current_user.projects
    return render_template('news_feed.html', posts=posts, projects=user_projects, user=current_user)

def landing_page():
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('landing_page.html', login_form=login_form, signup_form=signup_form)


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
        login_form = form)
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have logged out')
    return redirect(url_for("index"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(form.username.data, form.email.data,
                form.password.data)
        flash('Creating account')
        #try:
        db.session.add(user)  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
        #except:
        #   db.session.rollback()  # @UndefinedVariable
        login_user(user, remember=True)
        return redirect(url_for('edit_profile', status='first'))
    return render_template('signup.html', signup_form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(status=None):
    user=current_user
    form = ProfileForm()
    previous_page = config.ROOT_URL
    form.old_username = user.username
    profile_pic_url = user.profile_pic_url
    file_name = user.get_profile_pic_file_name()
    if user.profile_pic_url is None:
        profile_pic_url = config.DEFAULT_PROFILE_PIC_URL
    if request.method == 'POST' and form.validate_on_submit():
        profile_pic_url = get_s3_url(file_name)
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.location = form.location.data
        user.profile_pic_url = request.form['file_upload_url']
        
#         if pic and allowed_file(pic.filename):
#                 filename = secure_filename(pic.filename)
#                 profile_pic = resize_image(filename, width=config.PROFILE_PIC_WIDTH)
#                 thumbnail = resize_image(pic, width=config.THUMBNAIL_SIZE)
#                 AK = config.AWS_ACCESS_KEY_ID
#                 SK = config.AWS_SECRET_ACCESS_KEY
#                 conn = boto.connect_s3()
#                 b=conn.get_bucket(config.AWS_S3_BUCKET)
#                 k=b.new_key()
#                 k.key = username+'-profile_pic.png'
#                 k.set_contents_from_string(profile_pic.getvalue())              
        db.session.add(user)  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
        return redirect(previous_page)
    else:
        form = ProfileForm(username=user.username, first_name=user.first_name, last_name=user.last_name, location=user.location)
   
    return render_template('edit_profile.html', form=form, status=status, user=user, previous_page=previous_page, profile_pic_url=profile_pic_url, file_name=file_name)

@app.route('/<username>')
@login_required
def user_profile():
    projects = Project.query.filter_by(lead==current_user.id).limit(config.PROJ_LIST_LIMIT)  # @UndefinedVariable
    return render_template('user_profile.html', user=current_user, projects=projects)

@app.route('/<username>/<project_id>/edit')
@login_required
def edit_project(project_id):
    project = Project.query.filter_by(id=int(project_id))  # @UndefinedVariable
    form = ProjectCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        project.name = form.project_name
        project.goal = form.project_goal
        project.privacy = form.project_privacy
        db.session.add(project)  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
    return render_template('edit_project.html', project=project)

@app.route('/create_project')
@login_required
def create_project():
    form =ProjectCreateForm()
    previous_page = config.ROOT_URL
    if request.method == 'POST' and form.validate_on_submit():
        project = Project(form.project_name, form.project_goal, form.project_privacy, form.created_by)
        db.session.add(project)  # @UndefinedVariable
        project_id = db.session.flush()  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
        return redirect(url_for('edit_project'), project_id=project_id)
    
    return render_template('create_project.html', form=form, previous_page=previous_page)
    
@app.route('/project/<project_id>/')
def project_page(project_id):
    project = Project.query.filter_by(id=project_id)  # @UndefinedVariable
    return render_template('project_page.html', project=project, root_url=config.ROOT_URL)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username= username).first()  # @UndefinedVariable
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', username = username))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('user', username = username))
    session.add(u)
    session.commit()
    flash('You are now following ' + username + '!')
    return redirect(url_for('user', username = username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(User.username == username).first()  # @UndefinedVariable
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', username = username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('user', username = username))
    session.add(u)
    session.commit()
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('user', username = username))

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