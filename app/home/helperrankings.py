# app/home/helperrankigns.py
import os

from flask import redirect, render_template, url_for, request, flash
from flask_login import login_required, current_user
from twilio.rest import Client
from .. import db
from . import home
from .. models import League, Team, Event, Ranking
from .helper import get_count, check_admin_user, round_to_three, admin_and_user_leagues

def ranking_table(league_name):

    # Retrieve data on the number of games, number of teams, and qualifiers for the league
    total_teams = League.query.filter_by(league_name=league_name).first().number_of_total_teams
    number_of_teams = get_count(Team.query.filter_by(league_name=league_name))
    team_queries = Team.query.filter_by(league_name=league_name)

    # Determine Wins, Loss, WL Differentials for each team
    team_DWL, sorted_team_differentials, sorted_team_wins, sorted_team_losses = determine_team_diff_wins_losses(team_queries)

    # Determine order of teams based upon differentials
    team_names_ranked = order_rankings(team_queries, team_DWL, sorted_team_differentials, number_of_teams)

    number_of_qualifiers = League.query.filter_by(league_name=league_name).first().number_of_qualifiers
    final_stats = determine_ranking_statistics(number_of_qualifiers, team_names_ranked,
                                               team_DWL, number_of_teams,
                                               sorted_team_wins, sorted_team_losses,
                                               league_name, total_teams)

    teamindex = 0
    while teamindex < number_of_teams:
        current_team = final_stats[teamindex]
        ranking_entry = Ranking.query.filter_by(league=league_name, team=current_team['name']).first()

        # If ranking does not exit
        if ranking_entry is None:
            newranking = Ranking(
                place = current_team['place'],
                league = league_name,
                team = current_team['name'],
                wins = current_team['wins'],
                losses = current_team['losses'],
                percent = current_team['winning percentage'],
                games_behind = current_team['games_behind'],
                magic_number = current_team['magic'],
                status = current_team['status']
                )

            try:
                # Add league to the database
                db.session.add(newranking)
                db.session.commit()
                #flash('You have successfully added a new rankings entry.')
            except:
                # in case league name already exists
                flash('Error: entry not added')

        else:
            # If ranking does exist
            ranking_entry.league = league_name
            ranking_entry.place = current_team['place']
            ranking_entry.team = current_team['name']
            ranking_entry.wins = current_team['wins']
            ranking_entry.losses = current_team['losses']
            ranking_entry.percent = current_team['winning percentage']
            ranking_entry.games_behind = current_team['games_behind']
            ranking_entry.magic_number = current_team['magic']
            ranking_entry.status = current_team['status']

            try:
                # Add league to the database
                db.session.commit()
                #flash('You have successfully updated an old ranking entry.')
            except:
                # in case league name already exists
                flash('Ranking entry not added')
        teamindex += 1
    # Indented
    return


def determine_magic_status(team_wins, first_out_max_wins, team_losses, last_in_max_losses, magic_number_with_losses, qualifiers, rank):
    """ This function determines the magic number and the playoff eligibility status for a team. """

    if team_wins > first_out_max_wins:
        status = 'IN'
        magic = '-'
    elif team_losses > last_in_max_losses:
        status = 'OUT'
        magic = '-'
    else:
        status = 'ALIVE'
        if rank > qualifiers:
            magic = '-'
        else:
        # Determines 'Magic Number' for teams to qualify
            magic = magic_number_with_losses - team_wins

    return status, magic


def games_behind(leader_differential, team_wins, team_losses):
    """ This function takes in a team's wins & losses and the leader's differential and determines the team's games behind. """
    games_behind_leader = (leader_differential - (team_wins - team_losses)) / 2.0
    #if games_behind_leader == 0:
    #    games_behind_leader = '-'
    return games_behind_leader


def validate_playoff_information(qualifiers, games, number_of_registered_teams, total_teams):
    """ This function determines if enough details have been entered to determine playoff information for a league. """
    if qualifiers is None or games is None or total_teams is None:
        return False
    if number_of_registered_teams != total_teams:
        return False
    return True


# Determine the ranking of the teams based upon their season results
def order_rankings(list_of_teams, ranking_data, differentials, number_of_teams):
    not_stored = True
    for team in list_of_teams:
        # For the team in question, gets the W-L differential
        team_diff = ranking_data[team.name]['differential']
        not_stored = True
        # For each team available, checks to see if jth best differential
        # matches team differential
        for j in range(number_of_teams):
            current_diff = differentials[j]
            if (current_diff == team_diff) and (not_stored is True):
                # Gives the matching team that ran
                differentials[j] = team.name
                # Creates list of rankings
                not_stored = False
    ranked_teams_list = differentials
    return ranked_teams_list

# Determine the initial rankings based upon the wins and losses
# First gets wins, losses, and W-L differentials for each team
def determine_team_diff_wins_losses(list_of_teams):
    ranking_data = {}
    differentials = []
    winsall = []
    lossesall = []
    for team in list_of_teams:
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

    return ranking_data, differentials, winsall, lossesall

# Determine the advanced statistics for each team's season and playoff status
def determine_ranking_statistics(number_of_qualifiers, differentials,
                                 ranking_data, number_of_teams, ordered_wins,
                                 ordered_losses, league_name, total_teams):

    leader_differential = ranking_data[differentials[0]]['differential']
    season_games = League.query.filter_by(league_name=league_name).first().number_of_games

    # Determine if league information has been entered into League Table
    information = validate_playoff_information(number_of_qualifiers, season_games, number_of_teams,
                                      total_teams)

    if information is True:
        first_out_least_possible_losses = ordered_losses[number_of_teams - number_of_qualifiers - 1]
        last_in_least_possible_wins = ordered_wins[number_of_qualifiers-1]
        first_out_max_wins = season_games - first_out_least_possible_losses
        last_in_max_losses = season_games - last_in_least_possible_wins
        magic_number_with_losses = season_games - first_out_least_possible_losses + 1

    # If including win percentage, account for a team that hasn't played yet (division by 0)
    final_data = {}
    current_ranking = 1
    # test the winning percentage branch
    for rank in range(number_of_teams):
        name = differentials[rank]
        final_team = ranking_data[name]
        team_wins = (ranking_data[name]['wins'])
        team_losses = (ranking_data[name]['losses'])
        final_team['wins'] = team_wins
        final_team['losses'] = team_losses
        final_team['name'] = name
        # Add winning percentage to team dictionary
        final_team['winning percentage'] = round_to_three(team_wins, team_losses)

        # Add games behind to team dictionary
        final_team['games_behind'] = games_behind(leader_differential, team_wins, team_losses)

        # Add team's rank to each team dictionary -- allows for ties between teams with the same record
        if ((rank != 0) and (final_data[rank-1]['games_behind'] == final_team['games_behind'])):
            final_team['place'] = current_ranking
        else:
            current_ranking = rank + 1
            final_team['place'] = current_ranking

        # Determine Magic & Status
        if information is True:
            final_team['status'], final_team['magic'] = determine_magic_status(team_wins, first_out_max_wins, team_losses,
                                                        last_in_max_losses, magic_number_with_losses, number_of_qualifiers, current_ranking)
        else:
            final_team['magic'] = False
            final_team['status'] = False

        final_data[rank] = final_team
    results = final_data
    return results
