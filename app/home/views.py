# app/home/views.py

from flask import abort, render_template, session
from flask_login import current_user, login_required
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct

from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")

@home.route('/admin/<league_name>')
@login_required
def admin_dashboard(league_name):

    def enough_teams(league_name):

        def get_count(q):
            count_q = q.statement.with_only_columns([func.count()]).order_by(None)
            count_x = q.session.execute(count_q).scalar()
            return (count_x)

        teamcount = get_count(Team.query.filter_by(league_name=league_name))
        team_requirement = League.query.filter_by(league_name=league_name).first().number_of_total_teams

        if (teamcount == team_requirement):
            ranking_criteria = True
        else:
            ranking_criteria = False

        return(ranking_criteria)

    session['ranking_criteria'] = enough_teams(league_name)

    return render_template('home/admin_dashboard.html', title=league_name, league_name=league_name)
