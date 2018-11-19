# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

from app import db, login_manager

class User(UserMixin, db.Model):
    """
    Create an User table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id_number = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    phone_number = db.Column(db.String(10), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        """
        Prevents the pasword from ever being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Team(db.Model):
    """
    Create a Team table
    """

    __tablename__ = 'teams'

    id_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), unique=True)
    division_name = db.Column(db.String(60))
    conference_name = db.Column(db.String(60))
    league_id = db.Column(db.String(60), db.ForeignKey('leagues.id_number'), nullable=False)
    league_id_constraint = relationship("League", foreign_keys=[league_id])
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

    def __repr__(self):
        return '<Team: {}>'.format(self.name)

class Event(db.Model):
    """
    Create an event table
    """

    __tablename__ = 'events'

    id_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day = db.Column(db.Date())
    winner_id = db.Column(db.String(200), db.ForeignKey('teams.id_number'), nullable=False)
    loser_id = db.Column(db.String(200), db.ForeignKey('teams.id_number'), nullable=False)
    league_id = db.Column(db.String(60), db.ForeignKey('leagues.id_number'), nullable=False)
    league_id_constraint = relationship("League", foreign_keys=[league_id])
    winner_id_constraint = relationship("Team", foreign_keys=[winner_id])
    loser_id_constraint = relationship("Team", foreign_keys=[loser_id])
    winning_score = db.Column(db.Integer)
    losing_score = db.Column(db.Integer)

    def __repr__(self):
        return '<Event: {}>'.format(self.id)

class League(db.Model):
    """
    Create an leagues table
    """

    __tablename__ = 'leagues'

    id_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    league_name = db.Column(db.String(200), unique=True)
    number_of_games = db.Column(db.Integer)
    number_of_conferences = db.Column(db.Integer)
    number_of_total_teams = db.Column(db.Integer)
    number_of_rounds = db.Column(db.Integer)
    number_of_qualifiers = db.Column(db.Integer)
    is_byes = db.Column(db.String(200))


    def __repr__(self):
        return '<League: {}>'.format(self.name)

class Ranking(db.Model):
    """
    Create a Ranking table
    """

    __tablename__ = 'rankings'

    id_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.String(200), db.ForeignKey('teams.id_number'), nullable=False)
    team_constraint = relationship("Team", foreign_keys=[team_id])
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    games_played = db.Column(db.Integer)

    def __repr__(self):
        return '<Ranking: {}>'.format(self.name)

class Update(db.Model):
    """
    Create a table for users who have multiple leagues
    """

    __tablename__ = 'updates'

    id_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(60), db.ForeignKey('users.username'), nullable=False)
    #first_name = db.Column(db.String(60), index=True)
    #last_name = db.Column(db.String(60), index=True)
    username_constraint = relationship("User", foreign_keys=[username])
    league_name = db.Column(db.String(60), db.ForeignKey('leagues.id_number'), nullable=False)
    league_constraint = relationship("League", foreign_keys=[league_name])
    phone_number = db.Column(db.String(10), index=True, unique=True)
    is_admin = db.Column(db.String(200))

    def __repr__(self):
        return '<Update: {}>'.format(self.username)
