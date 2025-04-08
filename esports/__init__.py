from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from esports.config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.session_protection = "strong"
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from esports.users.routes import users
    from esports.posts.routes import posts
    from esports.main.routes import main
    from esports.errors.handlers import errors
    from esports.team.routes import team
    from esports.schools.routes import schools
    from esports.devices.routes import devices
    from esports.games.routes import games
    from esports.players.routes import players
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(team)
    app.register_blueprint(schools)
    app.register_blueprint(devices)
    app.register_blueprint(games)
    app.register_blueprint(players)

    return app
