# app/home/__init__.py

from flask import Blueprint

home = Blueprint('home', __name__)

from . import views
from . import leagueviews
from . import teamviews
from . import eventviews
from . import userviews
from . import rankingviews
