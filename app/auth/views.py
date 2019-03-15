# app/auth/views.py

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user, fresh_login_required

from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User, Registration
from ..home.helper import check_admin_user, admin_and_user_leagues
from ..home.helperrankings import ranking_table

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                        username=form.username.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        phone_number=form.phone_number.data,
                        password=form.password.data)

        # add user to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        print("BLUE1", current_user, current_user.is_authenticated)

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        # check whether user exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # log user in
            login_user(user)

            if current_user.is_authenticated:
                admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

                # # Display rankings
                # for league in admin_leagues:
                #     ranking_table(league)
                #
                # for league in user_leagues:
                #     ranking_table(league)

            # redirect to the appropriate dashboard page
            # if user.is_admin:
            return redirect(url_for('home.list_leagues'))
            #else:
            #    return redirect(url_for('home.dashboard'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    if current_user.is_authenticated:
        logout_user()

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log a user out through the logout link
    """
    logout_user()

    flash('You have successfully been logged out.')


    # redirect to the login page
    return redirect(url_for('auth.login'))
