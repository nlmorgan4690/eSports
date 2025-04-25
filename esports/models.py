from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
from esports import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)

    posts = db.relationship('Post', backref='author', lazy=True)
    teams_coached = db.relationship('Team', backref='coach', lazy=True)

    school = db.relationship('School', backref='users', foreign_keys=[school_id])


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"Role('{self.role}')"


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=True)

    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    players = db.relationship('Player', backref='school', lazy=True)
    teams = db.relationship('Team', backref='school', lazy=True)
    devices = db.relationship('Device', backref='school', lazy=True)
    networks = db.relationship('Network', backref='school', lazy=True)

    def __repr__(self):
        return f"School('{self.name}', '{self.location}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    game_icon = db.Column(db.String(200), unique=True, nullable=False)
    max_team_size = db.Column(db.Integer, nullable=False)

    players = db.relationship('Player', backref='game', lazy=True)
    player_links = db.relationship('PlayerGame', back_populates='game')

    def __repr__(self):
        return f"Game('{self.name}')"



class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    ad_username = db.Column(db.String(64), unique=True)
    ad_synced = db.Column(db.Boolean, default=False)
    _ad_passphrase = db.Column("ad_passphrase", db.Text)  # Encrypted storage

    games = db.relationship('PlayerGame', back_populates='player')
    teams = db.relationship('PlayerTeam', backref='player', cascade="all, delete-orphan")

    @property
    def ad_passphrase(self):
        from esports.players.fernet import decrypt_string
        return decrypt_string(self._ad_passphrase) if self._ad_passphrase else None

    @ad_passphrase.setter
    def ad_passphrase(self, value):
        from esports.players.fernet import encrypt_string
        self._ad_passphrase = encrypt_string(value)

    def __repr__(self):
        return f"Player('{self.name}')"


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    game = db.relationship('Game', backref='teams', lazy=True)  # ✅ add this
    players = db.relationship('PlayerTeam', backref='team', lazy=True)

    def __repr__(self):
        return f"Team('{self.name}')"



class PlayerTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"PlayerTeam('{self.player_id}', '{self.team_id}')"

class PlayerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    player = db.relationship('Player', back_populates='games')
    game = db.relationship('Game', back_populates='player_links')

    def __repr__(self):
        return f"PlayerGame(player_id={self.player_id}, game_id={self.game_id})"

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_mac = db.Column(db.String(17), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    ise_synced = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Device('{self.device_name}', '{self.device_mac}')"


class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    switch_name = db.Column(db.String(100), nullable=False)
    device_ip = db.Column(db.String(15), unique=True, nullable=False)

    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)

    def __repr__(self):
        return f"Network('{self.switch_name}', '{self.device_ip}')"


class Platform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform_icon = db.Column(db.String(200), unique=True, nullable=False)
    device_type = db.Column(db.String(50), unique=True, nullable=False)

    devices = db.relationship('Device', backref='platform', lazy=True)
    networks = db.relationship('Network', backref='platform', lazy=True)

    def __repr__(self):
        return f"Platform('{self.device_type}')"
