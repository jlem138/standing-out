from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from . import admin
from .. import db
from .forms import UpdateForm
from ..models import User, Update
from .helper import check_admin_user, get_count


@admin.route('/users/<leaguename>')
@login_required
def list_users(leaguename):
    """
    List all users
    """
    updates = Update.query.filter_by(league_name=leaguename).all()

    # finding usernames of all updated
    updated_entries = Update.query.filter_by(league_name=leaguename).all()
    admin_status = check_admin_user(leaguename)
    return render_template('admin/users/users.html', leaguename=leaguename,
                           admin_status=admin_status, updates=updates,
                           users_updated=updated_entries, title='Users')


@admin.route('/users/delete/<leaguename>/<username>', methods=['GET', 'POST'])
@login_required
def delete_user(username, leaguename):
    """
    Delete an entry from the update table
    """
    update_entry = Update.query.filter_by(league_name=leaguename, username=username).first()
    user_entry = User.query.filter_by(username=username)
    # Get number of entries that have the same username
    entries_count = get_count(Update.query.filter_by(league_name=leaguename))

    # if there is only 1 entry, then this is the only information the user has
    # so delete the user, first delete the update
    db.session.delete(update_entry)
    db.session.commit()
    if entries_count == 1:
        db.session.delete(user_entry)
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

    add_user = False

    form = UpdateForm()
    if form.validate_on_submit():
        update = Update(
            username="test2",
            league_name=leaguename,
            is_admin=True
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
    return render_template('admin/users/user.html', add_user=add_user,
                           form=form, title='Add User', leaguename=leaguename)

@admin.route('/users/edit/<leaguename>/<username>', methods=['GET', 'POST'])
@login_required
def edit_user(username, leaguename):
    """
    Edit a user
    """
    add_user = False

    update_entry = Update.query.filter_by(league_name=leaguename, username=username).first()
    form = UpdateForm(obj=update_entry)
    if form.validate_on_submit():
        update_entry.league_name = form.league_name.data
        if form.is_admin.data == "True":
            update_entry.is_admin = True
        elif form.is_admin.data == "False":
            update_entry.is_admin = False
        db.session.commit()
        flash('You have successfully edited the user.')
    #
    #     # redirect to the events page
        return redirect(url_for('admin.list_users', leaguename=leaguename))
    #
    #form.id.data = user.id
    form.league_name.data = update_entry.league_name
    # form.email.data = user.email
    # form.username.data = user.username
    # form.first_name.data = user.first_name
    # form.last_name.data = user.last_name
    # #form.password_hash.data = user.password_hash
    form.is_admin.data = update_entry.is_admin

    return render_template('admin/users/user.html', action="Edit",
                           add_user=add_user, form=form, leaguename=leaguename,
                           users_updated=update_entry, title="Edit user")
