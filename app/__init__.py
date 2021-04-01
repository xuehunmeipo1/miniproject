from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config')
    from app.service import cloudapp
    app.register_blueprint(cloudapp, url_prefix="/api/v1")
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()
    return app


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"message": "You are unauthorized to do the operation."}), 401
