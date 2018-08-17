# app/admin/__init__.py

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views

# imports the views form the teamviews.py file
from . import teamviews
from . import leagueviews
from . import eventviews
from . import userviews
from . import rankingviews
