# app/home/views.py

from flask import render_template, session
from flask_login import current_user, login_required
from ..models import Team, Event, League, User, Registration
from .helper import admin_and_user_leagues
from .helperrankings import ranking_table
from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """

    # Display user's admin leagues and user leagues
    if current_user.is_authenticated:
        admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    # Set admin and user leagues to None if no user is logged in
    else:
        admin_leagues = None
        user_leagues = None

    return render_template('home/index.html', title="Welcome",
                           admin_leagues=admin_leagues, user_leagues=user_leagues)

@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")
