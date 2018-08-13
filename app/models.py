# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

from app import db, login_manager

class Employee(UserMixin, db.Model):
    """
    Create an Employee table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """
        Prevent pasword from being accessed
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
        return '<Employee: {}>'.format(self.username)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

class Team(db.Model):
    """
    Create a Team table
    """

    __tablename__ = 'teams'

    name = db.Column(db.String(60), primary_key=True)
    division_name = db.Column(db.String(60))
    conference_name = db.Column(db.String(60))
    league_name = db.Column(db.String(60))

    def __repr__(self):
        return '<Team: {}>'.format(self.name)

class Event(db.Model):
    """
    Create an event table
    """

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date())
    winner = db.Column(db.String(200), db.ForeignKey('teams.name'), nullable=False)
    loser = db.Column(db.String(200), db.ForeignKey('teams.name'), nullable=False)
    winner_constraint = relationship("Team", foreign_keys=[winner])
    loser_constraint = relationship("Team", foreign_keys=[loser])
    winning_score = db.Column(db.Integer)
    losing_score = db.Column(db.Integer)

    def __repr__(self):
        return '<Event: {}>'.format(self.name)

class Detail(db.Model):
    """
    Create an details table
    """

    __tablename__ = 'details'

    id = db.Column(db.Integer, primary_key=True)
    number_of_conferences = db.Column(db.Integer)
    number_of_total_teams = db.Column(db.Integer)
    number_of_rounds = db.Column(db.Integer)
    number_of_qualifiers = db.Column(db.Integer)
    is_byes = db.Column(db.String(200))


    def __repr__(self):
        return '<Detail: {}>'.format(self.name)
