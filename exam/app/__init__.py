from flask import Flask
from flask_migrate import Migrate
from flask_login import current_user, LoginManager
import os

from app.models import db
from . import auth
from . import users, admin
from .models import User

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(admin.bp)
    app.route('/', endpoint='index')(users.index)

    return app