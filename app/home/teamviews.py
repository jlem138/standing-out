# Team Views

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import home
from .. import db
from . forms import TeamForm, TeamNoNameForm
from ..models import Team
from .helper import check_admin_user, admin_and_user_leagues


@home.route('/<league_name>/teams', methods=['GET', 'POST'])
@login_required
def list_teams(league_name):
    """
    List all teams
    """

    admin_status = check_admin_user(league_name)
    teams = Team.query.filter_by(league_name=league_name).all()

    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    return render_template('home/teams/teams.html', league_name=league_name,
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           teams=teams, league=league_name, title="Teams",
                           admin_status=admin_status)

@home.route('/<league_name>/teams/add', methods=['GET', 'POST'])
@login_required
def add_team(league_name):
    """
    Add a team to the database
    """

    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    team_add = True
    form = TeamForm()
    #entered_teams = Team.query.filter_by(league)
    if form.validate_on_submit():
        team = Team(name=form.name.data,
                    division_name=form.division_name.data,
                    conference_name=form.conference_name.data,
                    wins=0,
                    losses=0,
                    league_name=league_name)
        try:
            # add team to the database
            db.session.add(team)
            db.session.commit()
            flash('You have successfully added a new team.')
        except:
            # in case team name already exists
            flash('Team has already been registered for this league.')
            return redirect(url_for('home.list_teams', league_name=league_name))

        # redirect to teams page
        return redirect(url_for('home.list_teams', league_name=league_name))

    # load team template
    return render_template('home/teams/team.html', action="Add", admin_leagues=admin_leagues,
                           user_leagues=user_leagues, add_team=team_add, form=form,
                           league_name=league_name, title="Add Team")

@home.route('/<league_name>/teams/edit/<teamname>', methods=['GET', 'POST'])
@login_required
def edit_team(teamname, league_name):
    """
    Edit a team
    """

    admin_status = check_admin_user(league_name)

    team_add = False
    team = Team.query.get_or_404(teamname)
    game_count = team.wins + team.losses
    if game_count > 0:
        form = TeamNoNameForm(obj=team)
    else:
        form = TeamForm(obj=team)

    if form.validate_on_submit():
        if game_count == 0:
            team.name = form.name.data
        team.name = form.name.data
        team.division_name = form.division_name.data
        team.conference_name = form.conference_name.data
        team.league_name = league_name
        db.session.commit()
        flash('You have successfully edited the team.')

        # redirect to the teams page
        return redirect(url_for('home.list_teams', league_name=league_name))

    if game_count == 0:
        team.name = form.name.data
    form.division_name.data = team.division_name
    form.conference_name.data = team.conference_name
    form.name.data = team.name


    # Leagues for which current user is an admin or standard user
    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)


    return render_template('home/teams/team.html', action="Edit", user_leagues=user_leagues,
                           admin_leagues=admin_leagues, league_name=league_name, team_add=team_add,
                           admin_status=admin_status, form=form, teamname=teamname,
                           title="Edit Team")


@home.route('/<league_name>/teams/delete/<teamname>', methods=['GET', 'POST'])
@login_required
def delete_team(teamname, league_name):
    """
    Delete a team from the database
    """
    team = Team.query.filter_by(name=teamname).first()

    db.session.delete(team)
    db.session.commit()
    flash('You have successfully deleted the team.')

    # Redirect to the Teams page
    return redirect(url_for('home.list_teams', league_name=league_name))
