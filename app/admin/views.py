# app/admin/views.py

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
