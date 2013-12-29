from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_envvar('PROJLOG_SETTINGS', silent=True)


#if __name__ == '__main__':
#    app.run()