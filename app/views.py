from app import app, db, login_manager
from sqlalchemy.sql.expression import insert, select
import os
from functools import wraps
from forms import *
from flask import render_template, flash, redirect , Flask, url_for, request, g, session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from models import  FriendRequest, friendships, Notification, Post, PostComment
import config
from file_lib import *
import time, base64, urllib, json, hmac
from hashlib import sha1
from werkzeug.utils import secure_filename
from PIL import Image
from flask_wtf.csrf import CsrfProtect
csrf = CsrfProtect()


def notification_viewed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nid' in request.args:
            nid = request.args.get('nid')
            notif = db.session.query(Notification).get(nid) # @UndefinedVariable
            if not notif.seen:
                notif.seen=True
                db.session.add(notif)# @UndefinedVariable
                db.session.commit()# @UndefinedVariable
        return f(*args, **kwargs)
    return decorated_function
        

@app.route('/sign_s3_upload/')
def sign_s3():
    
    folder = config.S3_BUCKET_FOLDER

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
    
@csrf.error_handler
def csrf_error(reason):
    return render_template('csrf_error.html', reason=reason), 400


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
    user_projects = Project.query.filter_by(created_by_id=current_user.id).limit(config.PROJ_LIST_LIMIT)  # @UndefinedVariable
    return render_template('news_feed.html', posts=posts,  projects=user_projects)

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
    profile_pic_url = user.get_profile_pic_url()
    if 'status' in request.args.keys():
        status = request.args['status']
    temp_file_name = user.username
    if request.method == 'POST' and form.validate_on_submit():
        user.username = form.username.data.lower()
        user.first_name = form.first_name.data.lower().capitalize()
        user.last_name = form.last_name.data.lower().capitalize()
        user.location = form.location.data.lower().capitalize()
        user.gender = form.gender.data
        user.about = form.about.data
        user.privacy = form.privacy.data
        pic_file = request.files['picture']
        if pic_file and allowed_filename_pic(pic_file.filename):
            s3_filename = user.get_profile_pic_filename()
            save_picture_s3(pic_file,s3_filename, sizes=config.PROFILE_PIC_SIZES)    
        db.session.add(user)  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
        return redirect(url_for('user_page',username=user.username))
    else:
        form = ProfileForm(username=user.username, 
                           first_name=user.first_name, last_name=user.last_name,
                            location=user.location,
                            gender=user.gender,
                            about=user.about,
                            privacy=user.get_privacy())

    return render_template('edit_profile.html', 
                           form=form, status=status, user=user, 
                           previous_page=previous_page, 
                           profile_pic_url=profile_pic_url, 
                           file_name=temp_file_name)

@app.route('/user/<username>')
@login_required
def user_page(username):
    user = User.query.filter_by(username=username).first()# @UndefinedVariable
    if user is not None:
        if user.is_viewable_by(current_user.id):
            projects = Project.query.filter_by(created_by_id=user.id).all()  # @UndefinedVariable
            return render_template('user_page.html', user=user, projects=projects)
        else: 
            request_sent = FriendRequest.query.filter_by(requester_id=current_user.id, requested_id=user.id, approved=False, ignored=False).count() > 0 # @UndefinedVariable
            request_received = FriendRequest.query.filter_by(requester_id=user.id, requested_id=current_user.id, approved=False, ignored=False).count() > 0 # @UndefinedVariable
            return render_template('user_page_private.html', user=user, request_sent=request_sent,request_received=request_received)
    else:
        return redirect(url_for('index'))
    
@app.route('/my_friends')
@login_required
def my_friends():
    friends = current_user.friends.all()
    return render_template('my_friends.html',friends=friends)
    
    
@app.route('/request_friend', methods=['POST'])
def request_friend():  
    form = FriendRequestForm()
    if form.validate_on_submit():
        if request.method =='POST':
            requester_id =request.form['requester_id']
            requested_id =request.form['requested_id']
        count = FriendRequest.query.filter_by(requester_id=requester_id, requested_id=requested_id).count()# @UndefinedVariable
        #count_reverse = FriendRequest.query.filter_by(requester_id=requested_id, requested_id=requester_id).count()# @UndefinedVariable
        if count == 0:
            friend_request = FriendRequest(requester_id=requester_id, requested_id=requested_id)
            try:
                db.session.add(friend_request)# @UndefinedVariable
                db.session.commit()# @UndefinedVariable
            except:
                return "Error"
#     else:
#         return  render_template('add_friend_form.html',form=form)
    return "Success"

@app.route('/approve_friend', methods=['GET', 'POST'])
def approve_friend():  
    form = FriendApproveForm()
    if request.method =='POST' and form.validate_on_submit():
        requester_id = int(form.requester_id.data)
        requested_id = int(form.requested_id.data)
#     if 'requester_id' in request.args:
#         requester_id = request.args['requester_id']
#         requested_id = request.args['requested_id']
        approve_request = form.approve.data
        friend_request = FriendRequest.query.filter_by(requester_id=requester_id, requested_id=requested_id, ignored=False).first()# @UndefinedVariable
        if friend_request:
            if approve_request:
                ins1=friendships.insert().values(user_id=requester_id, friend_id=requested_id)# @UndefinedVariable
                ins2=friendships.insert().values(user_id=requested_id, friend_id=requester_id)# @UndefinedVariable
                db.engine.execute(ins1) #@UndefinedVariable
                db.engine.execute(ins2) #@UndefinedVariable
                friend_request.approved=True
            else:
                friend_request.approved=False
                friend_request.ignored=True
            try:
                db.session.add(friend_request)# @UndefinedVariable  
                db.session.commit()# @UndefinedVariable   
            except:
                return "Error"              
    #else:
#     requester_id = request.args['requested_id']
#     requested_id = request.args['requested_id']
#     approve_request = True#request.form['approve']
    return "Success"


@app.route('/friend_requests')
@login_required
@notification_viewed 
def friend_requests():
    requests = FriendRequest.query.filter_by(requested_id=current_user.id, approved=False,ignored=False).limit(10)# @UndefinedVariable
    
    return render_template('friend_requests.html',friend_requests=requests)
    



@app.route('/user/<username>/profile_pic/')
@login_required
def user_profile_pic_page(username):   
    user = User.query.filter_by(username=username).first()# @UndefinedVariable
    if user is not None:
        return render_template('user_profile_pic.html', user=user)
    else:
        redirect(url_for('index'))
        
        
        
@app.route('/post', methods=['GET', 'POST'])      
@login_required
def post():
    form = PostForm()
    user_id = current_user.id
    form.project_id.choices = [(p.id,p.project_name) for p in Project.query.filter_by(created_by_id=current_user.id).order_by(Project.created_date.desc()).limit(config.PROJ_LIST_LIMIT)]  # @UndefinedVariable
    if request.method =='POST' and form.validate_on_submit():
        project_id = int(request.form['project_id'])
        project = Project.query.get(project_id) # @UndefinedVariable
        if current_user.id == project.created_by_id:
            file=request.files['picture']
            create_post(project_id, current_user.id, form.post_text.data, file)
            return redirect(url_for('index'))
    return render_template('post.html',form=form)
            

def create_post(project_id, user_id, post_text, pic_file):
    post = Post(created_by_id=user_id,
                        project_id=project_id,
                        post_text=post_text
                        )
    if pic_file:
        s3_filename = generate_filename(current_user.username)
        post.pic_id=s3_filename
        save_picture_s3(pic_file,s3_filename, sizes=config.POST_PIC_SIZES)  
    db.session.add(post)  # @UndefinedVariable
    db.session.commit()  # @UndefinedVariable
    
            
@app.route('/ajax_post', methods=['GET', 'POST'])      
def ajax_post():
    form = PostFormAjax()
    if request.method =='POST' and form.validate_on_submit():
        project_id = form.project_id.data
        user_id = form.user_id.data
        post_text = form.post_text.data
        project = Project.query.get(project_id) # @UndefinedVariable
        pic_file=None
        if 'picture' in request.files:
            pic_file = request.files['picture']
        if user_id == project.created_by_id:
            create_post(project_id, user_id, post_text, pic_file)
            return "Success"
    return "Error: Form Validation"

@app.route('/post_comment', methods=['GET', 'POST'])  
def post_comment():
    if request.method =='POST':
        user_id = int(request.form['user_id'])
        post_id = int(request.form['post_id'])
        comment_text = request.form['comment_text']
    else:
        user_id = int(request.args['user_id'])
        post_id = int(request.args['post_id'])
        comment_text = request.args['comment']
    comment_text = comment_text.strip()
    user = User.query.get(user_id)# @UndefinedVariable
    post = Post.query.get(post_id)# @UndefinedVariable
    if user and post:
        project = Project.query.get(post.project_id)
        url = project.get_url() 
        comment = PostComment(user_id=user_id,post_id=post_id, 
                    comment_text=comment_text)
        db.session.add(comment)# @UndefinedVariable
        db.session.flush() # @UndefinedVariable
        notif_msg = user.get_full_name() +" commented on your post"
        dom_element_id = 'comment'+str(comment.id)
        notif = Notification(message=notif_msg, user_id=user_id, url=url, dom_element_id=dom_element_id)
        db.session.add(notif)# @UndefinedVariable
        db.session.commit()# @UndefinedVariable
        return '{"success":true,"comment_id":"'+str(comment.id)+'"}'
    else:
        return "{'success':false, 'error_msg':'Invalid user or post', 'post_id':"+str(post_id)+", 'user_id':"+str(user_id)+"}"

@app.route('/project/<project_id>/<slug>/', methods=['GET', 'POST'])
@login_required
def project_page(project_id, slug):
    project = Project.query.get(project_id) # @UndefinedVariable
    posts = Post.query.filter_by(project_id=project_id).order_by(Post.created_date.desc()).limit(10)# @UndefinedVariable
    viewable=project.is_viewable_by(current_user.id)
    form=PostForm()
    if request.method == 'POST' and form.validate_on_submit() :
        pic_file = request.files['picture']
        post_text = form.post_text.data
        user_id = current_user.id
        create_post(project_id, user_id, post_text, pic_file)
    return render_template('project_page.html', project=project, posts=posts, viewable=viewable, form=form)


@app.route('/project/<project_id>/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id, slug):
    project = Project.query.get(int(project_id))  # @UndefinedVariable
    form = ProjectForm()
    if request.method == 'POST' and form.validate_on_submit() : ##and project.created_by == current_user.id and form.validate_on_submit() :
        project.project_name = form.project_name.data
        project.goal = form.goal.data
        project.privacy_mode = form.privacy.data
        project.comments = form.comments.data
        file = request.files['picture']
        if file: ## and allowed_filename_pic(file.filename):   
            if not project.has_pic():
                prefix = project.get_slug()[:10]
                s3_filename = generate_filename(prefix)
                project.pic_id = s3_filename 
            save_picture_s3(file, project.pic_id, config.PROJ_PIC_SIZES)   
        db.session.add(project)  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
        path=project.get_path()
        return redirect(path)
    else:
        form = ProjectForm(project_name=project.project_name, 
                           goal=project.goal,
                           comments = project.comments,
                           privacy = project.privacy_mode)

    return render_template('edit_project.html', form=form, project=project)

@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    form =ProjectForm()
    form.created_by=current_user
    previous_page = config.ROOT_URL
    if request.method == 'POST' and form.validate_on_submit():
        project = Project(project_name=form.project_name.data, 
                          goal=form.goal.data, 
                          privacy=form.privacy.data,
                          created_by_id=current_user.id)
        db.session.add(project)  # @UndefinedVariable
        db.session.commit()  # @UndefinedVariable
        return redirect(project.get_path())
    return render_template('create_project.html', form=form, previous_page=previous_page)
    


@app.route('/follow/<username>')
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