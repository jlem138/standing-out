# Event Views

from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm
from ..models import Team, Event, League, User, Ranking
from sqlalchemy import func, distinct
from .helper import check_admin_user, check_admin, get_count

@admin.route('/events/<league_name>')
@login_required
def list_events(league_name):
    """
    List all events
    """

    admin_status=check_admin_user(league_name)
    events = Event.query.filter_by(league_name=league_name).all()

    return render_template('admin/events/events.html', league_name = league_name,
                           admin_status=admin_status,
                           events=events, title='Game Results')

@admin.route('events/add/<league_name>', methods=['GET', 'POST'])
@login_required
def add_event(league_name):
    """
    Add a event to the database
    """

    add_event = True

    form = EventForm()

    entered_teams = [(team.name, team.name) for team in Team.query.filter_by(league_name=league_name).all()]
    form.winner.choices = entered_teams
    form.loser.choices = entered_teams

    if form.validate_on_submit():
        event = Event(
        #id = form.id.data,
            day = form.day.data,
            winner = form.winner.data,
            loser = form.loser.data,
            league_name=league_name,
            winning_score = form.winning_score.data,
            losing_score = form.losing_score.data
            )

        winning_team_entry=Team.query.filter_by(name=event.winner).first()
        losing_team_entry=Team.query.filter_by(name=event.loser).first()

        winning_team_entry.wins = (str(int(winning_team_entry.wins)+1))
        losing_team_entry.losses = (str(int(losing_team_entry.losses)+1))

        try:
            db.session.add(event)
            db.session.commit()
            flash('You have successfully added a new event.')
        except:
            # in case event name already exists
            flash('Error: event name already exists.')

        # redirect to the events page
        return redirect(url_for('admin.list_events', league_name=league_name))

    # load event template
    return render_template('admin/events/event.html', add_event=add_event,
                           form=form, title='Add Game Result', league_name=league_name)

@admin.route('/events/edit/<league_name>/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(league_name, id):
    """
    Edit a event
    """

    add_event = False

    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)

    entered_teams = [(team.name, team.name) for team in Team.query.filter_by(league_name=league_name).all()]
    form.winner.choices = entered_teams
    form.loser.choices = entered_teams

    if form.validate_on_submit():
        #event.id = form.id.data

        previous_winning_team_entry=Team.query.filter_by(name=event.winner).first()
        previous_losing_team_entry=Team.query.filter_by(name=event.loser).first()

        #previous_winning_team_entry.wins = (str(int(previous_winning_team_entry.wins)-1))
        #previous_losing_team_entry.losses = (str(int(previous_losing_team_entry.losses)-1))

        event.day = form.day.data
        event.winner = form.winner.data
        event.loser = form.loser.data
        event.winning_score = form.winning_score.data
        event.losing_score = form.losing_score.data

        new_winning_team_entry=Team.query.filter_by(name=event.winner).first()
        new_losing_team_entry=Team.query.filter_by(name=event.loser).first()

        #new_winning_team_entry.wins = (str(int(new_winning_team_entry.wins)+1))
        #new_losing_team_entry.losses = (str(int(new_losing_team_entry.losses)+1))

        # If winner and loser are different teams, and score isn't the same
        if (event.winner != event.loser and int(event.winning_score) > int(event.losing_score)):
            try:
                previous_winning_team_entry.wins = (str(int(previous_winning_team_entry.wins)-1))
                previous_losing_team_entry.losses = (str(int(previous_losing_team_entry.losses)-1))
                new_winning_team_entry.wins = (str(int(new_winning_team_entry.wins)+1))
                new_losing_team_entry.losses = (str(int(new_losing_team_entry.losses)+1))
                db.session.commit()
                flash('You have successfully edited the event.')

            except:
                flash('The information you have entered is not correct')

            return redirect(url_for('admin.list_events', league_name=league_name))

        else:
            #flash('The winning and losing team you entered were the same')
            #return redirect(url_for('admin.edit_event', id=id, league_name=league_name))

        # redirect to the events page
            return render_template('admin/events/event.html', action="Edit",
                               add_event=add_event, form=form, league_name=league_name,
                               event=event, title="Edit Game Result")
    #form.id.data = event.id
    form.day.data = event.day
    form.winner.data = event.winner
    form.loser.data = event.loser
    form.winning_score.data = event.winning_score
    form.losing_score.data = event.losing_score

    return render_template('admin/events/event.html', action="Edit",
                           add_event=add_event, form=form, league_name=league_name,
                           event=event, title="Edit Game Result")


@admin.route('/events/delete/<league_name>/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(league_name, id):
    """
    Delete a event from the database
    """
    #check_admin()

    event = Event.query.get_or_404(id)

    winning_team_entry=Team.query.filter_by(name=event.winner).first()
    losing_team_entry=Team.query.filter_by(name=event.loser).first()

    winning_team_entry.wins = (str(int(winning_team_entry.wins)-1))
    losing_team_entry.losses = (str(int(losing_team_entry.losses)-1))

    db.session.delete(event)
    db.session.commit()
    flash('You have successfully deleted the event.')

    # redirect to the events page
    return redirect(url_for('admin.list_events', league_name=league_name))

    return render_template(title="Delete Game Result")
