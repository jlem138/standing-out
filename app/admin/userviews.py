from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm, UpdateForm
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct
from .helper import check_admin_user, check_admin, get_count


@admin.route('/users/<leaguename>')
@login_required
def list_users(leaguename):
    """
    List all users
    """
    updates = Update.query.filter_by(league_name=leaguename).all()

    current_username = current_user.username
    # finding usernames of all updated
    updated_entries = Update.query.filter_by(league_name=leaguename).all()
    admin_status = check_admin_user(leaguename)
    #if admin_status == '0':
    #    admin_status = False
    return render_template('admin/users/users.html', leaguename=leaguename,
    admin_status=admin_status, updates=updates, users_updated=updated_entries,
    current_username = current_username, title='Users')


@admin.route('/users/delete/<leaguename>/<username>', methods=['GET', 'POST'])
@login_required
def delete_user(username, leaguename):
    """
    Delete an entry from the update table
    """
    updateEntry = Update.query.filter_by(league_name=leaguename, username=username).first()
    userEntry = User.query.filter_by(username=username)
    # Get number of entries that have the same username
    entries_count = get_count(Update.query.filter_by(league_name=leaguename))

    # if there is only 1 entry, then this is the only information the user has, so delete the user, first delete the update
    db.session.delete(updateEntry)
    db.session.commit()
    if entries_count == 1:
        db.session.delete(userEntry)
        db.session.commit()

    flash('You have successfully deleted the update.')

    # redirect to the events page
    return redirect(url_for('admin.list_users', leaguename=leaguename))

    return render_template(title="Delete users")

@admin.route('user/add/<leaguename>', methods=['GET', 'POST'])
@login_required
def add_user(leaguename):
    """
    Add a user to the updated list of leagues
    """

    add_user = True

    form = UpdateForm()
    if form.validate_on_submit():
        if form.is_admin.data == '1':
            current_is_admin = '1'
        else:

        #elif form.is_admin.data == '0':
            current_is_admin = '0'
        #if 1==1:
        #    current_is_admin = True
        #print("GO", current_is_admin)
        userEntry = User.query.filter_by(username=form.username.data).all()
        user_first_name = userEntry.first_name
        user_last_name = userEntry.last_name
        user_phone_number = userEntry.phone_number
        update = Update(
            username=form.username.data,
            first_name=user_first_name,
            last_name=user_last_name,
            league_name=leaguename,
            phone_number=user_phone_number,
            is_admin=current_is_admin
            )
        try:
            # add event to the database
            db.session.add(update)
            db.session.commit()
            flash('You have successfully added a new user to this league')
        except:
            # in case event name already exists
            flash('Error: user name already exists.')

        # redirect to the events page
        return redirect(url_for('admin.list_users', leaguename=leaguename))

    # load event template
    return render_template('admin/users/user.html', add_user=add_user, form=form, title='Add User', leaguename=leaguename)

@admin.route('/users/edit/<leaguename>/<username>', methods=['GET', 'POST'])
@login_required
def edit_user(username, leaguename):
    """
    Edit a user
    """
    add_user = False
    updateEntry = Update.query.filter_by(league_name=leaguename, username=username).first()
    form = UpdateForm(obj=updateEntry)
    if form.validate_on_submit():
        updateEntry.username = form.username.data
        userEntry = User.query.filter_by(username=form.username.data).first()
        updateEntry.first_name = userEntry.first_name
        updateEntry.last_name = userEntry.last_name
        #updateEntry.is_admin = form.is_admin.data
        print("DATA-ONE", form.is_admin.data)
        if form.is_admin.data == 'True':
            updateEntry.is_admin = '1'
        elif form.is_admin.data == 'False':
            updateEntry.is_admin = '0'
        print("DATA7777", updateEntry.is_admin)
        db.session.commit()
        flash('You have successfully edited the user.')
    #     # redirect to the events page
        return redirect(url_for('admin.list_users', leaguename=leaguename))
    #
    form.username.data = updateEntry.username
    if updateEntry.is_admin == '1':
        form.is_admin.data = '1'
    elif updateEntry.is_admin == '0':
        form.is_admin.data = '0'

    return render_template('admin/users/user.html', action="Edit",
                           add_user=add_user, form=form,leaguename=leaguename,
                           users_updated=updateEntry, title="Edit User")
