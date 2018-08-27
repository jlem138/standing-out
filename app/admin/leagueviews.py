
# League views

from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm, UpdateForm
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct
from .helper import check_admin

# League Views

@admin.route('/leagues/add', methods=['GET', 'POST'])
@login_required
def add_league():
    """
    Add a league to the database
    """
    check_admin()

    add_league = True

    form = LeagueForm()
    if form.validate_on_submit():
        league = League(
                    name = form.name.data,
                    number_of_games = form.number_of_games.data,
                    number_of_conferences=form.number_of_conferences.data,
                    number_of_total_teams = form.number_of_total_teams.data,
                    number_of_rounds = form.number_of_rounds.data,
                    number_of_qualifiers = form.number_of_qualifiers.data,
                    is_byes = form.is_byes.data
                    )

        try:
            # add team to the database
            db.session.add(league)
            db.session.commit()
            flash('You have successfully added a new league.')
        except:
            # in case team name already exists
            flash('Error: league already exists.')

        # redirect to teams page
        return redirect(url_for('admin.list_leagues'))

    # load team template
    return render_template('admin/leagues/league.html', action="Add",add_league=add_league, form=form, title="Addx League")


@admin.route('/leagues', methods=['GET', 'POST'])
@login_required
def list_leagues():
    """
    List all leagues
    """

    current_username = current_user.username
    leagues_held_by_user_entries = Update.query.filter_by(username=current_username).all()

    user_league_list = []
    for entry in leagues_held_by_user_entries:
        user_league_list.append(entry.league_name)

    leagues = League.query.filter(League.name.in_(user_league_list)).all()

    return render_template('admin/leagues/leagues.html', title="leagues", leagues=leagues)


@admin.route('/leagues/delete/<leaguename>', methods=['GET', 'POST'])
@login_required
def delete_league(leaguename):
    """
    Delete a league from the database
    """
    check_admin()

    league = League.query.get_or_404(leaguename)
    db.session.delete(league)
    db.session.commit()
    flash('You have successfully deleted the league.')

    # redirect to the events page
    return redirect(url_for('admin.list_leagues'))

    return render_template(title="Delete Leagues")


@admin.route('/leagues/edit/<leaguename>', methods=['GET', 'POST'])
@login_required
def edit_league(leaguename):
    """
    Edit a league
    """
    check_admin()

    add_league = False

    league = League.query.get_or_404(leaguename)
    form = LeagueForm(obj=league)
    if form.validate_on_submit():
        league.name = form.name.data
        league.number_of_conferences = form.number_of_conferences.data
        league.number_of_games = form.number_of_games.data
        league.number_of_total_teams = form.number_of_total_teams.data
        league.number_of_rounds = form.number_of_rounds.data
        league.number_of_qualifiers = form.number_of_qualifiers.data
        league.is_byes = form.is_byes.data
        db.session.commit()
        flash('You have successfully edited the league.')

        # redirect to the events page
        return redirect(url_for('admin.list_leagues'))

    form.name.data = league.name
    form.number_of_conferences.data = league.number_of_conferences
    form.number_of_games.data = league.number_of_games
    form.number_of_total_teams.data = league.number_of_total_teams
    form.number_of_rounds.data = league.number_of_rounds
    form.number_of_qualifiers.data = league.number_of_qualifiers
    form.is_byes.data = league.is_byes

    return render_template('admin/leagues/league.html', action="Edit", add_league=add_league, form=form,
    leaguename=leaguename, title="Edit League")
