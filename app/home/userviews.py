from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import home
from .. import db
from .forms import UpdateForm
from ..models import League, User, Update
from .helper import check_admin_user, admin_and_user_leagues


@home.route('/<league_name>/users')
@login_required
def list_users(league_name):
    """
    List all users for the given league
    """

    # All update entries for the particular league
    updates = Update.query.filter_by(league_name=league_name).all()
    current_username = current_user.username

    # Check the admin status to be passed to html page
    # Admin status to be used to denote ability to edit another user
    admin_status = check_admin_user(league_name)

    # Leagues for which current user is an admin or standard user
    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]

    return render_template('home/users/users.html', league_name=league_name,
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           admin_status=admin_status, updates=updates,
                           current_username=current_username, title='Users')


@home.route('/<league_name>/users/delete/<username>', methods=['GET', 'POST'])
@login_required
def delete_user(username, league_name):
    """
    Delete an entry from the update table
    """
    update_entry = Update.query.filter_by(league_name=league_name, username=username).first()

    # Delete update from table
    db.session.delete(update_entry)
    db.session.commit()

    flash('You have successfully deleted the update.')

    # Redirect to the Users page page once the user is deleted from league
    return redirect(url_for('home.list_users', league_name=league_name))

@home.route('/<league_name>/user/add', methods=['GET', 'POST'])
@login_required
def add_user(league_name):
    """
    Add a user to the updated list of leagues
    """

    user_add = True

    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]

    form = UpdateForm()
    if form.validate_on_submit():
        if form.is_admin.data == 'True':
            current_is_admin = '1'
        else:
            current_is_admin = '0'

        user_entry = User.query.filter_by(username=form.username.data).first()
        updated_entries = Update.query.filter_by(username=form.username.data,
                                                 league_name=league_name).first()

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
                # Add Update to the database
                #league = League.query.get(league_name)
                #league.updates_for_league.append(update)
                db.session.add(update)
                db.session.commit()
                flash('You have successfully added a new user to this league')
            except:
                # in case event name already exists
                flash('Error: user name already exists.')

        # redirect to the events page
        return redirect(url_for('home.list_users', league_name=league_name))

    # load event template
    return render_template('home/users/user.html', add_user=user_add, form=form,
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           title="Invite User", league_name=league_name)

@home.route('/<league_name>/users/edit/<username>', methods=['GET', 'POST'])
@login_required
def edit_user(username, league_name):
    """
    Edit a user
    """
    user_add = False
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
        # redirect to the events page
        return redirect(url_for('home.list_users', league_name=league_name))

    form.username.data = update_entry.username
    if update_entry.is_admin == '1':
        form.is_admin.data = '1'
    elif update_entry.is_admin == '0':
        form.is_admin.data = '0'


    # Leagues for which current user is an admin or standard user
    league_lists = admin_and_user_leagues(current_user.username)
    user_leagues = league_lists[0]
    admin_leagues = league_lists[1]


    return render_template('home/users/user.html', action="Edit", user_leagues=user_leagues,
                           admin_leagues=admin_leagues, user_add=user_add, form=form,
                           league_name=league_name, users_updated=update_entry, title="Edit User")
