from flask import render_template, flash, redirect, url_for, request, session
from app import app, query_db, add_account, create_connection, login
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm, RegisterForm, LoginForm
from datetime import datetime
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from config import User, RC_SITE_KEY, RC_SECRET_KEY
# from egnefunksjoner import fileType
import os


app.config['RECAPTCHA_PUBLIC_KEY'] = RC_SITE_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RC_SECRET_KEY
# broken access control
@login.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM Users WHERE id="{}";'.format(user_id), one=True)
    if user == None:
        return None
    else:
        return User(user_id, user[1])

@login.unauthorized_handler
def unauthorized_callback():
    flash("uauthorized")
    return redirect(url_for("index"))



# functions
def fileType(filename):
    fil = filename.split(".")[-1]
    # if len(filename.split(".")) == 2:
    return fil

#check for valid letters
def is_valid(text):
    alphabet = "abcdefghijklmnopqrstuvwxyzæøå1234567890 /_:;-()[].,¨^@*´`!#$%&|\\"
    for char in text:
        # char.lower() makes sure the text is lowercase, otherwise "Hello" would not be valid because capital H wasn't in the alphabet.
        if char.lower() not in alphabet:
            return False
    else: # We've finished iterating, which means all characters were in the alphabet.
        return True

#variables
database = r"./database.db"
    
# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    if current_user.is_authenticated:
        return redirect(url_for('stream', username=current_user.username))
    if form.login.validate_on_submit() and form.login.submit.data:
        if is_valid(form.login.username.data):
            user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
            # conn = create_connection(database)
            # user = select_account(conn, form.login.username.data)
            flash("Remember to never share account details with anyone!")
            print(user)
            # conn.close()
            if user == None:
                flash('Sorry, this user does not exist!')
            elif check_password_hash(user['password'] ,form.login.password.data):
            # if form.login.validate_on_submit():
                login_form = LoginForm()
                us = load_user(user['id'])
                login_user(us, remember=login_form.remember_me.data)
                return redirect(url_for('stream', username=form.login.username.data))
            else:
                flash('Sorry, wrong password!')
        else:
            flash("you have illegal characters")

    elif form.register.is_submitted() and form.register.submit.data:
    # elif form.register.validate_on_submit() and form.register.submit.data: # får ikke denne linjen til å virke :( da blir det vanskelig met captcha og sjekking av lengde av ord osv :(

        if is_valid(form.register.username.data):
            user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.register.username.data), one=True)
            if user != None:
                flash("Username is already taken, please choose a different one")
            elif form.register.password.data != form.register.confirm_password.data:
                flash("Passwords are not equal")
            else:
                conn = create_connection(database)  
                add_account(conn, form.register.username.data, form.register.first_name.data, form.register.last_name.data, generate_password_hash(form.register.password.data))
                conn.close()
                # query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
                # form.register.last_name.data, generate_password_hash(form.register.password.data)))
                return redirect(url_for('index'))
        else:
            flash("you have illegal characters")
    print("im not in")
    return render_template('index.html', title='Welcome', form=form)

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    if username != current_user.get_username():
        return redirect(url_for('stream', username=current_user.get_username()))
    form = PostForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        filtype = fileType(form.image.data.filename)
        okFiler = ['png', 'jpeg', 'jgp', '']
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)

        if filtype in okFiler and is_valid(form.content.data) and form.content.data != "":
            query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
            return redirect(url_for('stream', username=username))
        else:
            flash("sorry this file format is not allowed")

    posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required

def comments(username, p_id):
    if username != current_user.get_username():
        return redirect(url_for('comments', username=current_user.get_username()))
    form = CommentsForm()
    if form.comment.data == "":
        flash("Your comment is empty")
    elif form.is_submitted() and is_valid(form.comment.data):
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))
    else:
        flash("You have used illegal characters")
    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required

def friends(username):
    if username != current_user.get_username():
        return redirect(url_for('friends', username=current_user.get_username()))
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted() and form.username.data == "":
        flash("You must enter a name")
    elif form.is_submitted() and form.username.data == current_user.get_username():
        flash("You can not be friends with yourself silly")
    elif form.is_submitted() and is_valid(form.username.data):
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    elif form.is_submitted() and is_valid(form.username.data) == False:
        flash("You have used illegal characters")
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required

def profile(username):
    form = ProfileForm()
    if username == current_user.get_username():

        if form.is_submitted() and is_valid(form.education.data) and is_valid(form.employment.data) and is_valid(form.music.data) and is_valid(form.movie.data) and is_valid(form.nationality.data):
            query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
                form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
            ))
            return redirect(url_for('profile', username=username))
        
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        return render_template('profile.html', title='profile', username=username, user=user, form=form, autheticated=True)
    else:
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        return render_template('profile.html', title='profile', username=username, user=user, form=form, autheticated=False)
    