# views.py

from flask import render_template, session
from flask_login import current_user, login_required, fresh_login_required
from ..models import Team, Event, League, User, Update
from .helper import admin_and_user_leagues
from .helperrankings import ranking_table


from app import app

@app.route('/')
def index():
    print("FOX1")
    league_lists = admin_and_user_leagues(current_user.username)
    admin_leagues = league_lists[0]
    user_leagues = league_lists[1]

    for league in admin_leagues:
        ranking_table(league)

    for league in user_leagues:
        ranking_table(league)

    print("FOX2")

    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")
