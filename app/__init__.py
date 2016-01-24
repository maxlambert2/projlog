from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect
import os

app = Flask(__name__)
app.config.from_envvar('PROJLOG_SETTINGS')
csrf = CsrfProtect(app)
db = SQLAlchemy(app)
 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
 
from app import views, models
 
if __name__ == '__main__':
      app.run()