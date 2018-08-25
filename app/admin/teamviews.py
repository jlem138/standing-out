# Team Views

from flask import flash, redirect, render_template, url_for, session
from flask_login import login_required

from . import admin
from .. import db
from . forms import TeamForm
from ..models import Team
from .helper import enough_teams, check_admin_user


@admin.route('/teams/<leaguename>', methods=['GET', 'POST'])
@login_required
def list_teams(leaguename):
    """
    List all teams
    """

    admin_status = check_admin_user(leaguename)
    teams = Team.query.all()

    return render_template('admin/teams/teams.html', leaguename=leaguename,
                           teams=teams, league=leaguename, title="teams",
                           admin_status=admin_status)


@admin.route('/teams/<leaguename>/add', methods=['GET', 'POST'])
@login_required
def add_team(leaguename):
    """
    Add a team to the database
    """
    #check_admin()

    add_team = True
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data,
                    division_name=form.division_name.data,
                    conference_name=form.conference_name.data,
                    league_name=form.league_name.data)
        try:
            # add team to the database
            db.session.add(team)
            db.session.commit()
            flash('You have successfully added a new team.')
        except:
            # in case team name already exists
            flash('Error: team name already exists.')

        ranking_criteria = enough_teams(leaguename)
        session['ranking_criteria'] = ranking_criteria
        # redirect to teams page
        return redirect(url_for('admin.list_teams', leaguename=leaguename,
                                ranking_criteria=ranking_criteria))

    # load team template
    return render_template('admin/teams/team.html', action="Add",
                           add_team=add_team, form=form, leaguename=leaguename,
                           title="Add Team")

@admin.route('/teams/<leaguename>/edit/<teamname>', methods=['GET', 'POST'])
@login_required
def edit_team(teamname, leaguename):
    """
    Edit a team
    """
    admin_status = check_admin_user(leaguename)

    add_team = False

    team = Team.query.get_or_404(teamname)
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.division_name = form.division_name.data
        team.conference_name = form.conference_name.data
        team.league_name = form.league_name.data
        db.session.commit()
        flash('You have successfully edited the team.')

        # redirect to the teams page
        return redirect(url_for('admin.list_teams', leaguename=leaguename))

    form.name.data = team.name
    form.division_name.data = team.division_name
    form.conference_name.data = team.conference_name
    form.league_name.data = team.league_name
    return render_template('admin/teams/team.html', action="Edit",
                           leaguename=leaguename, add_team=add_team,
                           admin_status=admin_status, form=form,
                           teamname=teamname, title="Edit Team")


@admin.route('/teams/<leaguename>/delete/<teamname>', methods=['GET', 'POST'])
@login_required
def delete_team(teamname, leaguename):
    """
    Delete a team from the database
    """
    check_admin()

    team = Team.query.get_or_404(teamname)
    db.session.delete(team)
    db.session.commit()
    flash('You have successfully deleted the team.')

    ranking_criteria = enough_teams(leaguename)
    session['ranking_criteria'] = ranking_criteria

    # redirect to the teams page
    return redirect(url_for('admin.list_teams', leaguename=leaguename,
                            ranking_criteria=ranking_criteria))

    return render_template(title="Delete Team")
