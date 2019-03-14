from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, fresh_login_required

from . import home
from .. import db
from .forms import RegistrationForm
from ..models import League, User, Registration
from .helper import check_admin_user, admin_and_user_leagues


@home.route('/<league_name>/users')
def list_users(league_name):
    """
    List all users for the given league
    """

    # All registration entries for the particular league
    registrations = Registration.query.filter_by(league_name=league_name).all()
    current_username = current_user.username

    # Check the admin status to be passed to html page
    # Admin status to be used to denote ability to edit another user
    admin_status = check_admin_user(league_name)

    # Leagues for which current user is an admin or standard user
    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    return render_template('home/users/users.html', league_name=league_name,
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           admin_status=admin_status, registrations=registrations,
                           current_username=current_username, title='Users')


@home.route('/<league_name>/users/delete/<username>', methods=['GET', 'POST'])
@login_required
def delete_user(username, league_name):
    """
    Delete an entry from the Registration table
    """
    registration_entry = Registration.query.filter_by(league_name=league_name, username=username).first()

    # Delete registration from table
    db.session.delete(registration_entry)
    db.session.commit()

    flash('You have successfully deleted the registration.')

    # Redirect to the Users page page once the user is deleted from league
    return redirect(url_for('home.list_users', league_name=league_name))

@home.route('/<league_name>/user/add', methods=['GET', 'POST'])
@login_required
def add_user(league_name):
    """
    Add a user to the updated list of leagues
    """

    user_add = True

    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    form = RegistrationForm()
    if form.validate_on_submit():
        if form.is_admin.data == 'True':
            current_is_admin = '1'
        else:
            current_is_admin = '0'

        user_entry = User.query.filter_by(username=form.username.data).first()

        registration_entries = Registration.query.filter_by(username=form.username.data,
                                                 league_name=league_name).first()

        if user_entry is None:
            flash('The entered username must belong to a registered user.')
        elif registration_entries is not None:
            flash('This user has already been entered for this league.')
        else:
            user_first_name = user_entry.first_name
            user_last_name = user_entry.last_name
            user_phone_number = user_entry.phone_number
            registration = Registration(
                username=form.username.data,
                league_name=league_name,
                phone_number=user_phone_number,
                is_admin=current_is_admin
                )
            try:
                # Add Registration to the database
                db.session.add(registration)
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
    registration_entry = Registration.query.filter_by(league_name=league_name, username=username).first()
    form = RegistrationForm(obj=registration_entry)
    if form.validate_on_submit():
        registration_entry.username = form.username.data
        user_entry = User.query.filter_by(username=form.username.data).first()
        registration_entry.first_name = user_entry.first_name
        registration_entry.last_name = user_entry.last_name
        if form.is_admin.data == 'True':
            registration_entry.is_admin = '1'
        elif form.is_admin.data == 'False':
            registration_entry.is_admin = '0'
        db.session.commit()
        flash('You have successfully edited the user.')
        # redirect to the events page
        return redirect(url_for('home.list_users', league_name=league_name))

    form.username.data = registration_entry.username
    if registration_entry.is_admin == '1':
        form.is_admin.data = '1'
    elif registration_entry.is_admin == '0':
        form.is_admin.data = '0'


    # Leagues for which current user is an admin or standard user
    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)


    return render_template('home/users/user.html', action="Edit", user_leagues=user_leagues,
                           admin_leagues=admin_leagues, user_add=user_add, form=form,
                           league_name=league_name, users_updated=registration_entry, title="Edit User")
