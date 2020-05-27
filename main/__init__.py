from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = '3b81a7164a731c013a39bcdad657becb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

from main import routes