from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, UpdateForm
from ..models import Team, Event, League, User, Update
from sqlalchemy import func, distinct

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

def check_admin_user(league_name):
    current_username = current_user.username
    status_updates = Update.query.filter_by(league_name=league_name, username=current_username).all()

    for status in status_updates:
        if ((status.username == current_username) and (status.is_admin == '1')):
            return '1'
    return '0'

def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count_x = q.session.execute(count_q).scalar()
    return count_x

def enough_teams(league_name):
    teamcount = get_count(Team.query.filter_by(league_name=league_name))
    team_requirement = League.query.filter_by(league_name=league_name).first().number_of_total_teams

    if (teamcount == team_requirement):
        ranking_criteria = True
    else:
        ranking_criteria = False

    return(ranking_criteria)

def round_to_three(wins, losses):
    games = (1.0 * wins) + losses
    return(format(wins/games, '0.3f'))

def admin_and_user_leagues(username):
    updates = Update.query.filter_by(username=username).all()
    user_leagues = []
    admin_leagues = []
    for update in updates:
        admin_status = check_admin_user(update.league_name)
        if admin_status is True:
            admin_leagues.append(update.league_name)
        else:
            user_leagues.append(update.league_name)
    return(admin_leagues, user_leagues)
