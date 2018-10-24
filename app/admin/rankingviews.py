# app/admin/rankings.py
import os

from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm, UpdateForm
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct, MetaData, engine, Table, create_engine, select
from .database import database_engine
from .helper import get_count, enough_teams, check_admin_user, check_admin, round_to_three
from twilio.rest import Client


@admin.route('/rankings/<leaguename>', methods=['GET', 'POST'])
@login_required
def list_rankings(leaguename):
    """
    List all teams
    """
    engine = database_engine
    conn = engine.connect()

    admin_status = check_admin_user(leaguename)

    # Retrieve data on teh number of games, number of teams, and qualifiers for the league
    games = League.query.filter_by(name=leaguename).first().number_of_games
    number_of_teams = League.query.filter_by(name=leaguename).first().number_of_total_teams
    qualifiers = League.query.filter_by(name=leaguename).first().number_of_qualifiers

    teams = Team.query.filter_by(league_name=leaguename)

    ranking_data = {}
    differentials = []
    winsall = []
    lossesall = []
    ranking = {}
    place = 0
    # First gets wins, losses, and W-L differentials for each team
    for team in teams:
        team_data = {}
        wins = get_count(Event.query.filter_by(winner=team.name))
        losses = get_count(Event.query.filter_by(loser=team.name))
        team_data['wins'] = wins
        team_data['losses'] = losses
        wonloss = wins - losses
        team_data['differential'] = wonloss
        # Creates lists of wins, losses, and differentials
        differentials.append(wonloss)
        winsall.append(wins)
        lossesall.append(losses)
        # Adds a data dictionary for each team
        ranking_data[team.name] = team_data

    # Sorts the lists from most to least
    differentials.sort(reverse=True)
    winsall.sort(reverse=True)
    lossesall.sort(reverse=True)

    not_stored = True
    for team in teams:
        # For the team in question, gets the W-L differential
        team_diff = ranking_data[team.name]['differential']
        not_stored = True
        # For each team available, checks to see if jth best differential matches team differential
        for j in range(number_of_teams):
            current_diff = differentials[j]
            if (current_diff == team_diff) and (not_stored == True):
                # Gives the matching team that ran
                differentials[j] = team.name
                # Creates list of rankings
                ranking[j] = j
                not_stored = False
                print(j, team.name, current_diff, team_diff)

    # print("test line")
    print("Q", qualifiers)
    print(differentials)
    last_in = differentials[qualifiers-1]
    last_in_wins = ranking_data[last_in]['wins']
    last_in_losses = ranking_data[last_in]['losses']
    leader_differential = ranking_data[differentials[0]]['differential']

    first_out_least_possible_losses = lossesall[number_of_teams - qualifiers - 1]
    last_in_least_possible_wins = winsall[qualifiers-1]

    def zero_out(entry):
        if (type(entry) != int):
            return 0;
        else:
            return entry;

    # If including win percentage, account for a team that hasn't played yet (division by 0)
    consec_teams = 0
    prev_GB = -1
    final_data = {}
    current_ranking = 1
    # test the winning percentage branch
    for rank in range(number_of_teams):
        final_team = {}
        name = differentials[rank]
        team_wins = (ranking_data[name]['wins'])
        team_losses = (ranking_data[name]['losses'])
        final_team['name'] = name
        final_team['wins'] = team_wins
        final_team['losses'] = team_losses
        final_team['winning percentage'] = round_to_three(team_wins, team_losses)
        final_team['GB'] = (leader_differential - (team_wins - team_losses)) / 2.0
        if ((rank != 0) and (final_data[rank-1]['GB'] == final_team['GB'])):
           final_team['place'] = current_ranking
        else:
           current_ranking = ranking[rank]+1
           final_team['place'] = current_ranking
        magic_number = (games + 1) - (last_in_losses + team_wins) + 1
        final_team['magic'] = magic_number
        if (games - team_wins < first_out_least_possible_losses):
            playoff_marker = 'IN'
        elif (games - team_losses < last_in_least_possible_wins):
            playoff_marker = 'OUT'
        else:
            playoff_marker = 'ALIVE'
        final_team['eligible'] = playoff_marker
        final_data[rank] = final_team

    title = leaguename + " Rankings"

    #Create standings string:
    message = []
    for rank in range(number_of_teams):
        # add Rank
        message.append(str(rank+1))
        message.append(". ")
        message.append(final_data[rank]['name'])
        if (rank+1) != number_of_teams:
            message.append('\n')
    rankings_message=''.join(message)


    return render_template('admin/rankings/rankings.html', ranking=ranking,
    leaguename=leaguename, admin_status=admin_status, number_of_teams=number_of_teams,
    teams=teams,data=final_data, diffs=differentials, rankings_message=rankings_message,
    title=title)

@admin.route('/rankings/sendtext/<leaguename>/<rankings_message>', methods=['GET', 'POST'])
@login_required
def rankings_text(leaguename, rankings_message):

    admin_status = check_admin_user(leaguename)

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    personal_number = os.environ['PERSONAL_NUMBER']
    twilio_number = os.environ['TWILIO_NUMBER']

    client = Client(account_sid, auth_token)

    client.messages.create(
        to=personal_number,
        from_=twilio_number,
        body=rankings_message
    )

    title="FINISHED"

    return redirect(url_for('admin.list_rankings', leaguename=leaguename))
