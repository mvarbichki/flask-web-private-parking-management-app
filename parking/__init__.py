from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from os import environ as env
from flask_session import Session
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler


load_dotenv()

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the PostgresSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = env.get("DATABASE_URL")
# secret key
app.config["SECRET_KEY"] = env.get("SECRET_KEY")
# set session type
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
sess = Session(app)
# initialize the app with the extension
db.init_app(app)

login_manager = LoginManager(app)
# login route
login_manager.login_view = "login"
# login message
login_manager.login_message = "Login required"
login_manager.login_message_category = "info"

# Configure logging. Write dt - ERROR: message. File max size 10KB and keeping only 1 backup file
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
handler = RotatingFileHandler(filename="error.log",
                              maxBytes=10000,
                              backupCount=1
                              )
handler.setLevel(logging.ERROR)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# import routes
from parking import routes
