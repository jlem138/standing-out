# app/admin/forms.py

from flask_wtf import FlaskForm
from flask_login import current_user, login_required
from wtforms import StringField, SubmitField, RadioField, BooleanField
from wtforms.validators import DataRequired

class TeamForm(FlaskForm):
    """
    Form for admin to add or edit a team
    """

    name = StringField('Name', validators=[DataRequired()])
    division_name = StringField('Division Name', validators=[DataRequired()])
    conference_name = StringField('Conference Name', validators=[DataRequired()])
    #league_name = StringField('League Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class TeamNoNameForm(FlaskForm):
    """
    Form for admin to add or edit a team
    """

    division_name = StringField('Division Name', validators=[DataRequired()])
    conference_name = StringField('Conference Name', validators=[DataRequired()])
    #league_name = StringField('League Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RankingForm(FlaskForm):
    """
    Form for admin to add or edit a team
    """

    id = StringField('id', validators=[DataRequired()])
    losses = StringField('Ls', validators=[DataRequired()])
    gb = StringField('gb', validators=[DataRequired()])
    mnumber = StringField('mnumber', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EventForm(FlaskForm):
    """
    Form for admin to add or edit an event
    """
    #id = StringField('id', validators=[DataRequired()])
    day = StringField('Date', validators=[DataRequired()])
    winner = StringField('Winner', validators=[DataRequired()])
    loser = StringField('Loser', validators=[DataRequired()])
    winning_score = StringField('Winning Score', validators=[DataRequired()])
    losing_score = StringField('Losing Score', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LeagueForm(FlaskForm):
    """
    Form for admin to select postseason details
    """
    #name = StringField('Name', validators=[DataRequired()])
    number_of_games = StringField('Number of games in season', validators=[DataRequired()])
    number_of_conferences = StringField('Number of Conferences', validators=[DataRequired()])
    number_of_total_teams = StringField('Total Teams', validators=[DataRequired()])
    number_of_rounds = StringField('Number of Rounds', validators=[DataRequired()])
    number_of_qualifiers = StringField('Number of Qualifiers', validators=[DataRequired()])
    is_byes = RadioField('Playoff Byes', choices = [("Y",'Yes'),("N", 'No')])
    submit = SubmitField('Submit')


class UserForm(FlaskForm):
    """
    Form for admin to add user details
    """
    id = StringField('id', validators=[DataRequired()])
    #league_name = StringField('League Name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    is_admin = RadioField('Admin?', choices = [("True","True"),("False", "False")])
    submit = SubmitField('Submit')

class UpdateForm(FlaskForm):
    """
    Form for admin to add user details
    """
    #id = StringField('id', validators=[DataRequired()])
    #league_name = StringField('League Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    is_admin = RadioField('Does this user have Admin status?', choices = [("True","Yes"),("False", "No")])
    submit = SubmitField('Submit')
