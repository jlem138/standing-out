# Event Views

from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm
from ..models import Team, Event, League, User, Ranking
from sqlalchemy import func, distinct

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

@admin.route('/events/<leaguename>')
@login_required
def list_events(leaguename):
    #check_admin()
    """
    List all events
    """

    list_of_teams2 = Team.query.filter_by(league_name=leaguename).all()
    #events_test = Event.query.filter(Event.winner.in_(list_of_teams2.name)).all()
    teamlist = []
    for item in list_of_teams2:
        teamlist.append(item.name)

    print("TEAM LIST", list_of_teams2)
    print("TEAM LIST2", teamlist)
    list_of_teams_in_league = Team.query.filter_by(league_name=leaguename)
    events = Event.query.filter(Event.winner.in_(teamlist)).all()
    #[next(s for s in events if s.winner == team) for team in list_of_teams_in_league]
    return render_template('admin/events/events.html', leaguename = leaguename,
                           events=events, title='Events')

@admin.route('events/add/<leaguename>', methods=['GET', 'POST'])
@login_required
def add_event(leaguename):
    """
    Add a event to the database
    """
    #check_admin()

    add_event = True

    form = EventForm()
    if form.validate_on_submit():
        event = Event(
        #id = form.id.data,
            day = form.day.data,
            winner = form.winner.data,
            loser = form.loser.data,
            winning_score = form.winning_score.data,
            losing_score = form.losing_score.data)

        try:
            # add event to the database
            db.session.add(event)
            db.session.commit()
            flash('You have successfully added a new event.')
        except:
            # in case event name already exists
            flash('Error: event name already exists.')

        # redirect to the events page
        return redirect(url_for('admin.list_events', leaguename=leaguename))

    # load event template
    return render_template('admin/events/event.html', add_event=add_event, form=form, title='Add Event', leaguename=leaguename)

@admin.route('/events/edit/<leaguename>/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(leaguename, id):
    """
    Edit a event
    """
    #check_admin()

    add_event = False

    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        #event.id = form.id.data
        event.day = form.day.data
        event.winner = form.winner.data
        event.loser = form.loser.data
        event.winning_score = form.winning_score.data
        event.losing_score = form.losing_score.data
        db.session.commit()
        flash('You have successfully edited the event.')

        # redirect to the events page
        return redirect(url_for('admin.list_events', leaguename=leaguename))

    #form.id.data = event.id
    form.day.data = event.day
    form.winner.data = event.winner
    form.loser.data = event.loser
    form.winning_score.data = event.winning_score
    form.losing_score.data = event.losing_score

    return render_template('admin/events/event.html', action="Edit",
                           add_event=add_event, form=form, leaguename=leaguename,
                           event=event, title="Edit EventX")


@admin.route('/events/delete/<leaguename>/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(leaguename, id):
    """
    Delete a event from the database
    """
    check_admin()

    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('You have successfully deleted the event.')

    # redirect to the events page
    return redirect(url_for('admin.list_events', leaguename=leaguename))

    return render_template(title="Delete Event")
