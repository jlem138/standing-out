# app/admin/rankings.py
import os

from flask import redirect, render_template, url_for, request, flash
from flask_login import login_required, current_user, fresh_login_required

from twilio.rest import Client
from .. import db
from twilio.http.http_client import TwilioHttpClient
from . import home
from ..models import Team, Event, League, Registration, Ranking
from .helper import get_count, check_admin_user, round_to_three, admin_and_user_leagues
from .helperrankings import validate_playoff_information

@home.route('/<league_name>/tiebreakers', methods=['GET', 'POST'])
@login_required
def list_tie_breakers(league_name):
    """
    List all tie breakers
    """

    if request.method=='POST':
        result = list(request.form.getlist('options'))
        print("TIE8", result)

    # Find head-to-head matchups between teams selected
    events = Event.query.filter(Event.winner.in_(result) & Event.loser.in_(result))

    winners_dict = {}
    losers_dict = {}

    for team in result:
        winners_dict[team] = 0
        losers_dict[team] = 0

    for item in events:
        winners_dict[item.winner] += 1
        losers_dict[item.loser] += 1

    number_of_teams = len(result)
    percents = []
    team_percents = {}
    percent_teams = {}
    tie_diff = {}

    for team in result:
        wins = winners_dict[team]
        losses = losers_dict[team]
        pct = round_to_three(wins, losses)
        percents.append(pct)
        # Cant use percents, could get overridden
        percent_teams[team] = pct
        tie_diff[team] = [wins,losses]

    percents.sort(reverse=True)

    counter = 0
    tiebreaker_teams_ordered = {}
    while counter < number_of_teams:
        current_percent = percents[counter]
        for team in result:
            if team and percent_teams[team] == current_percent:
                tiebreaker_teams_ordered[team] = counter
                # Remove percent from percents list
                percents[counter] = -1
                current_percent = -1
                result[counter] = False
        counter += 1

    return render_template('home/rankings/rankings.html', ranking=numbered_ranks, percents=percents,
                           percent_teams=percent_teams, team_percents=team_percents,
                           tiebreaker_teams_ordered=tiebreaker_teams_ordered, user_leagues=user_leagues,
                           admin_leagues=admin_leagues, tiebreakers=True, league_name=league_name,
                           admin_status=admin_status, number_of_teams=number_of_teams, tie_diff=tie_diff,
                           teams=teams, data=final_stats_data, information=final_information,
                           rankings_message=message, title=title)


@home.route('/<league_name>/rankings', methods=['GET', 'POST'])
@login_required

def list_rankings(league_name):
    """
    List all teams
    """

    admin_status = check_admin_user(league_name)

    title = league_name + " Rankings"

    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    percents = {}
    ranked_teams = []

    rankings = Ranking.query.filter_by(league=league_name).order_by(Ranking.games_behind)
    number_of_ranked_teams = 0
    for rank in rankings:
        percents[rank.team] = format(rank.percent, '0.3f')
        ranked_teams.append(rank.team)
        number_of_ranked_teams += 1
        #rank.percent = format(rank.percent, '0.3f')

    message = create_standings_message(league_name)

    total_teams = League.query.filter_by(league_name=league_name).first().number_of_total_teams
    number_of_teams = get_count(Team.query.filter_by(league_name=league_name))
    number_of_qualifiers = League.query.filter_by(league_name=league_name).first().number_of_qualifiers
    season_games = League.query.filter_by(league_name=league_name).first().number_of_games
    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)


    information = validate_playoff_information(number_of_qualifiers, season_games, number_of_teams,
                                          total_teams)

    return render_template('home/rankings/rankings.html', rankings=rankings, data=True,
                           information=information, percents=percents,
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           league_name=league_name, admin_status=admin_status,
                           rankings_message=message, title=title)


@home.route('/rankings/sendtext/<league_name>/<rankings_message>', methods=['GET', 'POST'])
@login_required
def rankings_text(league_name, rankings_message):
    """ This function takes in a league and its message, sending designated league users the message. """

    # get league users
    league_users = Registration.query.filter_by(league_name=league_name).all()

    #proxy_client = TwilioHttpClient()
    #proxy_client.session.proxies = {'https': os.environ['https_proxy']}
    #client = Client(account_sid, auth_token, http_client=proxy_client)

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    #personal_number = os.environ['PERSONAL_NUMBER']
    twilio_number = os.environ['TWILIO_NUMBER']

    client = Client(account_sid, auth_token)

    # for every user in the registrations for the league, if their phone number is
    # registered then send that person a text with the standings

    for user in league_users:
        phone = user.phone_number
        if phone is not None and phone != '':
            to_number = "1"+phone

            client.messages.create(
                to=to_number,
                from_=twilio_number,
                body=rankings_message
                )

    return redirect(url_for('home.list_rankings', league_name=league_name))


def create_standings_message(league_name):
    """ This function takes in the order of the teams and creates the message to send the users. """
    message = []

    rankings = Ranking.query.filter_by(league=league_name).order_by(Ranking.games_behind)
    number_of_teams = get_count(rankings)

    team_number = 0
    for ranking_entry in rankings:
        # Concatenate Place with Team to create single line of message
        message.append(str(ranking_entry.place))
        message.append(". ")
        message.append(str(ranking_entry.team))
        team_number += 1
        # if not last team
        if team_number != number_of_teams:
            message.append('\n')

    rankings_message = ''.join(message)
    return rankings_message
