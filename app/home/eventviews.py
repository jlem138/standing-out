# Event Views

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, current_user

from . import home
from .. import db
from .forms import EventForm
from ..models import Team, Event
from .helper import check_admin_user, admin_and_user_leagues

@home.route('/<league_name>/events')
@login_required
def list_events(league_name):
    """
    List all events
    """

    admin_status = check_admin_user(league_name)
    events = Event.query.filter_by(league_name=league_name).all()

    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]

    return render_template('home/events/events.html', league_name = league_name,
                           admin_status=admin_status, user_leagues=user_leagues, admin_leagues=admin_leagues,
                           events=events, title='Game Results')

@home.route('/<league_name>/events/add', methods=['GET', 'POST'])
@login_required
def add_event(league_name):
    """
    Add a event to the database
    """

    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]

    add_event = True

    form = EventForm()

    entered_teams = [(team.name, team.name) for
                     team in Team.query.filter_by(league_name=league_name).all()]
    form.winner.choices = entered_teams
    form.loser.choices = entered_teams

    if form.validate_on_submit():
        event = Event(
            day=form.day.data,
            winner=form.winner.data,
            loser=form.loser.data,
            league_name=league_name,
            winning_score=form.winning_score.data,
            losing_score=form.losing_score.data
            )

        winning_team_entry = Team.query.filter_by(name=event.winner).first()
        losing_team_entry = Team.query.filter_by(name=event.loser).first()

        # Update wins and losses for the winning and losing teams
        winning_team_entry.wins = (str(int(winning_team_entry.wins)+1))
        losing_team_entry.losses = (str(int(losing_team_entry.losses)+1))

        if event.winner == event.loser:
            flash('The winner and loser must be different teams.')
        elif int(event.winning_score) <= int(event.losing_score):
            flash('The winning score must be greater than the losing score.')
        else:
            try:
                db.session.add(event)
                db.session.commit()
                flash('You have successfully added a new event.')
            except:
                # in case event name already exists
                flash('The data you have entered is incorrect.')

        # redirect to the events page
        return redirect(url_for('home.list_events', league_name=league_name))

    # load event template
    return render_template('home/events/event.html', add_event=add_event,user_leagues=user_leagues,
                            admin_leagues=admin_leagues, form=form, title='Add Game Result', league_name=league_name)

@home.route('/<league_name>/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(league_name, id):
    """
    Edit a event
    """

    add_event = False

    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)

    entered_teams = [(team.name, team.name) for team in
                     Team.query.filter_by(league_name=league_name).all()]
    form.winner.choices = entered_teams
    form.loser.choices = entered_teams

    if form.validate_on_submit():

        previous_winning_team_entry = Team.query.filter_by(name=event.winner).first()
        previous_losing_team_entry = Team.query.filter_by(name=event.loser).first()

        event.day = form.day.data
        event.winner = form.winner.data
        event.loser = form.loser.data
        event.winning_score = form.winning_score.data
        event.losing_score = form.losing_score.data

        new_winning_team_entry = Team.query.filter_by(name=event.winner).first()
        new_losing_team_entry = Team.query.filter_by(name=event.loser).first()

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

            return redirect(url_for('home.list_events', league_name=league_name))

    form.day.data = event.day
    form.winner.data = event.winner
    form.loser.data = event.loser
    form.winning_score.data = event.winning_score
    form.losing_score.data = event.losing_score

    # Leagues for which current user is an admin or standard user
    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]


    return render_template('home/events/event.html', action="Edit", user_leagues=user_leagues,
                           admin_leagues=admin_leagues, add_event=add_event,
                           form=form, league_name=league_name, event=event,
                           title="Edit Game Result")


@home.route('/<league_name>/events/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(league_name, id):
    """
    Delete a event from the database
    """
    #check_admin()

    event = Event.query.get_or_404(id)

    winning_team_entry = Team.query.filter_by(name=event.winner).first()
    losing_team_entry = Team.query.filter_by(name=event.loser).first()

    winning_team_entry.wins = (str(int(winning_team_entry.wins)-1))
    losing_team_entry.losses = (str(int(losing_team_entry.losses)-1))

    db.session.delete(event)
    db.session.commit()
    flash('You have successfully deleted the event.')

    # redirect to the events page
    return redirect(url_for('home.list_events', league_name=league_name))
