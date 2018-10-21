from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm, UpdateForm
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

def check_admin_user(leaguename):
    current_username = current_user.username
    status_users = User.query.filter_by(league_name=leaguename, username=current_username).all()
    #status_users = User.query.all()
    status_updates = Update.query.filter_by(league_name=leaguename, username=current_username).all()

    for status in status_updates:
        if ((status.username == current_username) and (status.is_admin == '1')):
            return '1'
    for status in status_users:
        if ((status.username == current_username) and (status.is_admin == '1')):
            return '1'
    return '0'

def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count_x = q.session.execute(count_q).scalar()
    return count_x


def enough_teams(leaguename):

    teamcount = get_count(Team.query.filter_by(league_name=leaguename))
    team_requirement = League.query.filter_by(name=leaguename).first().number_of_total_teams

    if (teamcount == team_requirement):
        ranking_criteria = True
    else:
        ranking_criteria = False

    return(ranking_criteria)
