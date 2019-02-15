# League views

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import home
from .. import db
from .forms import LeagueForm
from ..models import League, Update
from .helper import check_admin_user, admin_and_user_leagues

# League Views

@home.route('/leagues/add', methods=['GET', 'POST'])
@login_required
def add_league():
    """
    Add a league to the database
    """
    check_admin()

    add_league = True

    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]

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
            # Add league to the database
            db.session.add(league)
            db.session.commit()
            flash('You have successfully added a new league.')
        except:
            # in case league name already exists
            flash('Error: league already exists.')

        # redirect to League page
        return redirect(url_for('home.list_leagues'))

    # load team template
    return render_template('home/leagues/league.html', action="Add",add_league=add_league,
                            user_leagues=user_leagues, admin_leagues=admin_leagues,
                            form=form, title="Add League")


@home.route('/leagues', methods=['GET', 'POST'])
@login_required
def list_leagues():
    """
    List all leagues
    """

    current_username = current_user.username
    leagues_held_by_user_entries = Update.query.filter_by(username=current_username).all()

    at_least_one_admin = False
    user_league_list = []
    overall_statuses = {}
    for entry in leagues_held_by_user_entries:
        user_league_list.append(entry.league_name)
        status = check_admin_user(entry.league_name)
        overall_statuses[entry.league_name] = status

    league_lists = admin_and_user_leagues(current_user.username)
    admin_leagues = league_lists[0]
    user_leagues = league_lists[1]

    # Determine if admin's edit/delete column needs to be displayed
    at_least_one_admin = (len(admin_leagues) >= 1)

    leagues = League.query.filter(League.league_name.in_(user_league_list)).all()


    return render_template('home/leagues/leagues.html', title="Leagues",
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           overall_statuses=overall_statuses, leagues=leagues,
                           at_least_one_admin=at_least_one_admin)


# @home.route('/leagues/<league_name>/delete', methods=['GET', 'POST'])
# @login_required
# def delete_league(league_name):
#     """
#     Delete a league from the database
#     """
#     check_admin()
#
#     league = League.query.get_or_404(league_name)
#
#     db.session.delete(league)
#     db.session.commit()
#
#     flash('You have successfully deleted the league.')
#
#     # redirect to the leagues page
#     return redirect(url_for('home.list_leagues'))
#
#     return render_template(title="Delete League")


@home.route('/leagues/<league_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_league(league_name):
    """
    Edit a league
    """
    add_league = False

    league = League.query.get_or_404(league_name)
    form = LeagueForm(obj=league)
    if form.validate_on_submit():
        league.number_of_conferences = form.number_of_conferences.data
        league.number_of_games = form.number_of_games.data
        league.number_of_total_teams = form.number_of_total_teams.data
        league.number_of_rounds = form.number_of_rounds.data
        league.number_of_qualifiers = form.number_of_qualifiers.data
        league.is_byes = form.is_byes.data
        db.session.commit()
        flash('You have successfully edited the league.')

        # redirect to the leagues page
        return redirect(url_for('home.list_leagues'))

    form.number_of_conferences.data = league.number_of_conferences
    form.number_of_games.data = league.number_of_games
    form.number_of_total_teams.data = league.number_of_total_teams
    form.number_of_rounds.data = league.number_of_rounds
    form.number_of_qualifiers.data = league.number_of_qualifiers
    form.is_byes.data = league.is_byes

    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]

    return render_template('home/leagues/league.html', action="Edit",
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           add_league=add_league, form=form, league_name=league_name,
                           title="Edit League")
