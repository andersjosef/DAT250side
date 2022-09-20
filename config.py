import os
from flask_login import UserMixin

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {} # Might use this at some point, probably don't want people to upload any file type

class User(UserMixin):
    def __init__(self, id, username) -> None:
        self.id = id
        self.username = username
        self.authenticated = False

    def get_username(self):
        return self.username

    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.id