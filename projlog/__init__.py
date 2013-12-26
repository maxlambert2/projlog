from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config

app = Flask(__name__)
app.config.from_object('config.local')
app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

if __name__ == '__main__':
    app.run()