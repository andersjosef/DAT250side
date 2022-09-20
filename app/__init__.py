from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import sqlite3
from sqlite3 import Error
import os

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

# TODO: Handle login management better, maybe with flask_login?
login = LoginManager(app)
login.login_view = "login"

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code

### My AJ attempt ###
#### INSERT #########
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn
# Add account fikset mot sqlinjection
def add_account(conn, username, first_name, last_name, password):
    sql = ''' INSERT INTO Users(username, first_name, last_name, password)
              VALUES(?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (username, first_name, last_name, password))
        conn.commit()
    except Error as e:
        print(e)

# select account
# def select_account(conn, user):
#     cur = conn.cursor()
#     sql = '''SELECT * FROM Users WHERE username="%s";'''
#     tup = (user)
#     cur.execute(sql, tup)
#     accounts = {}
#     for (id, username, first_name, last_name, password, education, employment, music, movie, nationality, birthday) in cur:
#         accounts = { 
#             "id": id, 
#             "username": username, 
#             "first_name": first_name, 
#             "last_name": last_name, 
#             "password": password,
#             "education": education,
#             "employment": employment,
#             "music": music,
#             "movie": movie,
#             "nationality": nationality,
#             "birthday": birthday
#             }

#     return accounts



# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes