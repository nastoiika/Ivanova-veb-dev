import os

# pip install flask faker flask_login mysql-connector-python

from flask import Flask, request 
from flask_login import current_user 
from .db import DBConnector
from .repositories.visit_log_repository import VisitLogRepository

db = DBConnector()
visit_log_repository = VisitLogRepository(db)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)
    app.config['DEBUG'] = True
    
    if test_config:
        app.config.from_mapping(test_config)
    
    db.init_app(app)

    @app.before_request
    def log_visit():
        if request.path.startswith('/static'):
            return
        user_id = current_user.id if current_user.is_authenticated else None
        path = request.path
        visit_log_repository.add(path=path, user_id=user_id)

    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)
    auth.login_manager.init_app(app)

    from . import users
    app.register_blueprint(users.bp)
    app.route('/', endpoint='index')(users.index)

    from . import visitor_log
    app.register_blueprint(visitor_log.bp)

    return app