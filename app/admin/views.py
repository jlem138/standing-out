# app/admin/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import admin
from .. import db
from forms import TeamForm, EventForm, DetailForm, EmployeeForm
from ..models import Team, Event, Detail, Employee

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

# team Views

@admin.route('/teams', methods=['GET', 'POST'])
@login_required
def list_teams():
    """
    List all teams
    """
    check_admin()

    teams = Team.query.all()

    return render_template('admin/teams/teams.html',
                           teams=teams, title="teams")

@admin.route('/teams/add', methods=['GET', 'POST'])
@login_required
def add_team():
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
        return redirect(url_for('admin.list_teams'))

    # load team template
    return render_template('admin/teams/team.html', action="Add",
                           add_team=add_team, form=form,
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

@admin.route('/events')
@login_required
def list_events():
    check_admin()
    """
    List all events
    """
    events = Event.query.all()
    return render_template('admin/events/events.html',
                           events=events, title='Events')

@admin.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    """
    Add a event to the database
    """
    check_admin()

    add_event = True

    form = EventForm()
    if form.validate_on_submit():
        event = Event(id = form.id.data,
            date = form.date.data,
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
        return redirect(url_for('admin.list_events'))

    # load event template
    return render_template('admin/events/event.html', add_event=add_event, form=form, title='Add Event')

@admin.route('/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    """
    Edit a event
    """
    check_admin()

    add_event = False

    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.id = form.id.data
        event.date = form.date.data
        event.winner = form.winner.data
        event.loser = form.loser.data
        event.winning_score = form.winning_score.data
        event.losing_score = form.losing_score.data
        db.session.commit()
        flash('You have successfully edited the event.')

        # redirect to the events page
        return redirect(url_for('admin.list_events'))

    form.id.data = event.id
    form.date.data = event.date
    form.winner.data = event.winner
    form.loser.data = event.loser
    form.winning_score.data = event.winning_score
    form.losing_score.data = event.losing_score

    return render_template('admin/events/event.html', action="Edit",
                           add_event=add_event, form=form,
                           event=event, title="Edit EventX")


@admin.route('/events/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    """
    Delete a event from the database
    """
    check_admin()

    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('You have successfully deleted the event.')

    # redirect to the events page
    return redirect(url_for('admin.list_events'))

    return render_template(title="Delete Event")

@admin.route('/details/add', methods=['GET', 'POST'])
@login_required
def add_detail():
    """
    Add a team to the database
    """
    check_admin()

    add_detail = True

    form = DetailForm()
    if form.validate_on_submit():
        detail = Detail(id=form.id.data,
                    number_of_conferences=form.number_of_conferences.data,
                    number_of_total_teams = form.number_of_total_teams.data,
                    number_of_rounds = form.number_of_rounds.data,
                    number_of_qualifiers = form.number_of_qualifiers.data,
                    is_byes = form.is_byes.data
                    )

        try:
            # add team to the database
            db.session.add(detail)
            db.session.commit()
            flash('You have successfully added a new detail.')
        except:
            # in case team name already exists
            flash('Error: detail already exists.')

        # redirect to teams page
        return redirect(url_for('admin.list_details'))

    # load team template
    return render_template('admin/details/detail.html', action="Add",
                           add_detail=add_detail, form=form,
                           title="Addx Detail")


@admin.route('/details', methods=['GET', 'POST'])
@login_required
def list_details():
    """
    List all details
    """
    check_admin()

    details = Detail.query.all()

    return render_template('admin/details/details.html',
                           details=details, title="details")

@admin.route('/details/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_detail(id):
    """
    Delete a detail from the database
    """
    check_admin()

    detail = Detail.query.get_or_404(id)
    db.session.delete(detail)
    db.session.commit()
    flash('You have successfully deleted the detail.')

    # redirect to the events page
    return redirect(url_for('admin.list_details'))

    return render_template(title="Delete Details")


@admin.route('/details/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_detail(id):
    """
    Edit a detail
    """
    check_admin()

    add_detail = False

    detail = Detail.query.get_or_404(id)
    form = DetailForm(obj=detail)
    if form.validate_on_submit():
        detail.id = form.id.data
        detail.number_of_conferences = form.number_of_conferences.data
        detail.number_of_total_teams = form.number_of_total_teams.data
        detail.number_of_rounds = form.number_of_rounds.data
        detail.number_of_qualifiers = form.number_of_qualifiers.data
        detail.is_byes = form.is_byes.data
        db.session.commit()
        flash('You have successfully edited the detail.')

        # redirect to the events page
        return redirect(url_for('admin.list_details'))

    form.id.data = detail.id
    form.number_of_conferences.data = detail.number_of_conferences
    form.number_of_total_teams.data = detail.number_of_total_teams
    form.number_of_rounds.data = detail.number_of_rounds
    form.number_of_qualifiers.data = detail.number_of_qualifiers
    form.is_byes.data = detail.is_byes

    return render_template('admin/details/detail.html', action="Edit",
                           add_detail=add_detail, form=form,
                           detail=detail, title="Edit Detail")


@admin.route('/employees')
@login_required
def list_employees():
    """
    List all employees
    """
    check_admin()

    employees = Employee.query.all()
    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')



@admin.route('/employees/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_employee(id):
    """
    Delete a employee from the database
    """
    check_admin()

    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('You have successfully deleted the employee.')

    # redirect to the events page
    return redirect(url_for('admin.list_employees'))

    return render_template(title="Delete employees")


@admin.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    """
    Edit a employee
    """
    check_admin()

    add_employee = False

    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    if form.validate_on_submit():
        employee.id = form.id.data
    #     employee.email = form.email.data
    #     employee.username = form.username.data
    #     employee.first_name = form.first_name.data
    #     employee.last_name = form.last_name.data
    #     #mployee.password_hash = form.password_hash.data
        if form.is_admin.data == "True":
            employee.is_admin = True;
        elif form.is_admin.data == "False":
            employee.is_admin = False;
        db.session.commit()
        flash('You have successfully edited the employee.')
    #
    #     # redirect to the events page
        return redirect(url_for('admin.list_employees'))
    #
    form.id.data = employee.id
    # form.email.data = employee.email
    # form.username.data = employee.username
    # form.first_name.data = employee.first_name
    # form.last_name.data = employee.last_name
    # #form.password_hash.data = employee.password_hash
    form.is_admin.data = employee.is_admin

    return render_template('admin/employees/employee.html', action="Edit",
                           add_employee=add_employee, form=form,
                           employee=employee, title="Edit employee")
