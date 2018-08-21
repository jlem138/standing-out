# Team Views

from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from . forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm
from ..models import Team, Event, League, User, Ranking, Current
from sqlalchemy import func, distinct

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

@admin.route('/teams/<league>', methods=['GET', 'POST'])
@login_required
def list_teams(league):
    """
    List all teams
    """
    check_admin()
    teams = Team.query.all()

    return render_template('admin/teams/teams.html', current_league=league,
                           teams=teams, league=league, title="teams")


@admin.route('/teams/<league>/add', methods=['GET', 'POST'])
@login_required
def add_team(league):
    """
    Add a team to the database
    """
    check_admin()

    add_team = True

    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data,
                    division_name = form.division_name.data,
                    conference_name = form.conference_name.data,
                    league_name = form.league_name.data)
        try:
            # add team to the database
            db.session.add(team)
            db.session.commit()
            flash('You have successfully added a new team.')
        except:
            # in case team name already exists
            flash('Error: team name already exists.')

        # redirect to teams page
        return redirect(url_for('admin.list_teams', league=league))

    # load team template
    return render_template('admin/teams/team.html', action="Add",
                           add_team=add_team, form=form, current_league=league,
                           title="Add Team")

@admin.route('/teams/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit_team(name):
    """
    Edit a team
    """
    check_admin()

    add_team = False

    team = Team.query.get_or_404(name)
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.division_name = form.division_name.data
        team.conference_name = form.conference_name.data
        team.league_name = form.league_name.data
        db.session.commit()
        flash('You have successfully edited the team.')

        # redirect to the teams page
        return redirect(url_for('admin.list_teams'))

    form.name.data = team.name
    form.division_name.data = team.division_name
    form.conference_name.data = team.conference_name
    form.league_name.data = team.league_name
    return render_template('admin/teams/team.html', action="Edit",
                           add_team=add_team, form=form,
                           team=team, title="Edit Team")


@admin.route('/teams/delete/<name>', methods=['GET', 'POST'])
@login_required
def delete_team(name):
    """
    Delete a team from the database
    """
    check_admin()

    team = Team.query.get_or_404(name)
    db.session.delete(team)
    db.session.commit()
    flash('You have successfully deleted the team.')

    # redirect to the teams page
    return redirect(url_for('admin.list_teams'))

    return render_template(title="Delete Team")
