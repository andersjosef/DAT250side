from curses import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
from wtforms.fields.html5 import DateField
from app import app, query_db

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={'placeholder': 'First Name'})
    last_name = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={'placeholder': 'Last Name'})
    username = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username=username.data), one=True)
        if user != None:
            flash("that username is already taken")

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
