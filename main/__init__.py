import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

from main import routes
