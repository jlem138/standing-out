from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm
from ..models import Team, Event, League, User, Ranking, Current
from sqlalchemy import func, distinct

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)



@admin.route('/users/<league>')
@login_required
def list_users(league):
    """
    List all users
    """
    check_admin()

    users = User.query.all()
    return render_template('admin/users/users.html', current_league = league,
                           users=users, title='Users')



@admin.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """
    Delete a user from the database
    """
    check_admin()

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('You have successfully deleted the user.')

    # redirect to the events page
    return redirect(url_for('admin.list_users'))

    return render_template(title="Delete users")


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """
    Edit a user
    """
    check_admin()

    add_user = False

    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.id = form.id.data
        user.league_name = form.league_name.data
    #     user.email = form.email.data
    #     user.username = form.username.data
    #     user.first_name = form.first_name.data
    #     user.last_name = form.last_name.data
    #     #mployee.password_hash = form.password_hash.data
        if form.is_admin.data == "True":
            user.is_admin = True;
        elif form.is_admin.data == "False":
            user.is_admin = False;
        db.session.commit()
        flash('You have successfully edited the user.')
    #
    #     # redirect to the events page
        return redirect(url_for('admin.list_users'))
    #
    form.id.data = user.id
    form.league_name.data = user.league_name
    # form.email.data = user.email
    # form.username.data = user.username
    # form.first_name.data = user.first_name
    # form.last_name.data = user.last_name
    # #form.password_hash.data = user.password_hash
    form.is_admin.data = user.is_admin

    return render_template('admin/users/user.html', action="Edit",
                           add_user=add_user, form=form,
                           user=user, title="Edit user")
