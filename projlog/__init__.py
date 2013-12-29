from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_envvar('PROJLOG_SETTINGS')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from projlog import views

#if __name__ == '__main__':
#    app.run()