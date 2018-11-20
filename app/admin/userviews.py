from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm, UpdateForm
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct
from .helper import check_admin_user, check_admin, get_count


@admin.route('/users/<league_name>')
@login_required
def list_users(league_name):
    """
    List all users
    """
    updates = Update.query.filter_by(league_name=league_name).all()

    current_username = current_user.username
    # finding usernames of all updated
    updated_entries = Update.query.filter_by(league_name=league_name).all()

    # Check the admin status to be passed to html page
    admin_status = check_admin_user(league_name)

    return render_template('admin/users/users.html', league_name=league_name,
    admin_status=admin_status, updates=updates, users_updated=updated_entries,
    current_username = current_username, title='Users')


@admin.route('/users/delete/<league_name>/<username>', methods=['GET', 'POST'])
@login_required
def delete_user(username, league_name):
    """
    Delete an entry from the update table
    """
    update_entry = Update.query.filter_by(league_name=league_name, username=username).first()
    user_entry = User.query.filter_by(username=username)
    # Get number of entries that have the same username
    entries_count = get_count(Update.query.filter_by(league_name=league_name))

    # if there is only 1 entry, then this is the only information the user has, so delete the user, first delete the update
    db.session.delete(update_entry)
    db.session.commit()
    if entries_count == 1:
        db.session.delete(user_entry)
        db.session.commit()

    flash('You have successfully deleted the update.')

    # redirect to the events page
    return redirect(url_for('admin.list_users', league_name=league_name))

    return render_template(title="Delete users")

@admin.route('user/add/<league_name>', methods=['GET', 'POST'])
@login_required
def add_user(league_name):
    """
    Add a user to the updated list of leagues
    """

    add_user = True

    form = UpdateForm()
    if form.validate_on_submit():
        if form.is_admin.data == '1':
            current_is_admin = '1'
        else:
            current_is_admin = '0'
        user_entry = User.query.filter_by(username=form.username.data).first()
        updated_entries = Update.query.filter_by(username=form.username.data, league_name=league_name).first()
        if user_entry is None:
            flash('The entered username must belong to a registered user.')
        elif updated_entries is not None:
            flash('This user has already been entered for this league.')
        else:
            user_first_name = user_entry.first_name
            user_last_name = user_entry.last_name
            user_phone_number = user_entry.phone_number
            update = Update(
                username=form.username.data,
                first_name=user_first_name,
                last_name=user_last_name,
                league_name=league_name,
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
        return redirect(url_for('admin.list_users', league_name=league_name))

    # load event template
    return render_template('admin/users/user.html', add_user=add_user, form=form,
    title='Add User', league_name=league_name)

@admin.route('/users/edit/<league_name>/<username>', methods=['GET', 'POST'])
@login_required
def edit_user(username, league_name):
    """
    Edit a user
    """
    add_user = False
    update_entry = Update.query.filter_by(league_name=league_name, username=username).first()
    form = UpdateForm(obj=update_entry)
    if form.validate_on_submit():
        update_entry.username = form.username.data
        user_entry = User.query.filter_by(username=form.username.data).first()
        update_entry.first_name = user_entry.first_name
        update_entry.last_name = user_entry.last_name
        if form.is_admin.data == 'True':
            update_entry.is_admin = '1'
        elif form.is_admin.data == 'False':
            update_entry.is_admin = '0'
        db.session.commit()
        flash('You have successfully edited the user.')
    #     # redirect to the events page
        return redirect(url_for('admin.list_users', league_name=league_name))
    #
    form.username.data = update_entry.username
    if update_entry.is_admin == '1':
        form.is_admin.data = '1'
    elif update_entry.is_admin == '0':
        form.is_admin.data = '0'

    return render_template('admin/users/user.html', action="Edit",
                           add_user=add_user, form=form,league_name=league_name,
                           users_updated=update_entry, title="Edit User")
