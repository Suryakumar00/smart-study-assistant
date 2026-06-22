from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from config import Config
from models.database import db, User
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.notes import notes_bp
from routes.quiz import quiz_bp
from routes.planner import planner_bp
from routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    @login_required
    def index():
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
