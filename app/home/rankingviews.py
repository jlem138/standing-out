# app/admin/rankings.py
import os

from flask import redirect, render_template, url_for
from flask_login import login_required, current_user

from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
from . import home
from ..models import Team, Event, League, Registration
from .helper import get_count, check_admin_user, round_to_three, admin_and_user_leagues

@home.route('/<league_name>/rankings', methods=['GET', 'POST'])
@login_required
def list_rankings(league_name):
    """
    List all teams
    """

    admin_status = check_admin_user(league_name)

    # Retrieve data on the number of games, number of teams, and qualifiers for the league
    number_of_teams = get_count(Team.query.filter_by(league_name=league_name))
    teams = Team.query.filter_by(league_name=league_name)
    total_teams = League.query.filter_by(league_name=league_name).first().number_of_total_teams

    # Determine the initial rankings based upon the wins and losses
    # First gets wins, losses, and W-L differentials for each team
    def collect_ranking_data(list_of_teams):
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

        return[ranking_data, differentials, winsall, lossesall]

    # Determine the ranking of the teams based upon their season results
    def order_rankings(list_of_teams, ranking_data, differentials):
        not_stored = True
        ranking = {}
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
                    ranking[j] = j
                    not_stored = False
        return([differentials, ranking])

    # Determine the advanced statistics for each team's season and playoff status
    def determine_ranking_statistics(number_of_qualifiers, differentials,
                                     ranking_data, number_of_teams, ordered_wins,
                                     ordered_losses, ranking):

        leader_differential = ranking_data[differentials[0]]['differential']
        season_games = League.query.filter_by(league_name=league_name).first().number_of_games

        information = playoff_information(number_of_qualifiers, season_games, number_of_teams,
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
            final_team['name'] = name
            # Add winning percentage to team dictionary
            final_team['winning percentage'] = round_to_three(team_wins, team_losses)

            # Add games behind to team dictionary
            final_team['GB'] = games_behind(leader_differential, team_wins, team_losses)

            # Add team's rank to each team dictionary -- allows for ties between teams with the same record
            if ((rank != 0) and (final_data[rank-1]['GB'] == final_team['GB'])):
                final_team['place'] = current_ranking
            else:
                current_ranking = ranking[rank]+1
                final_team['place'] = current_ranking

            if information:
                # Determines 'Magic Number' for teams to qualify
                final_team['magic'] = magic_number_with_losses - team_wins

                # Determine team playoff status
                final_team['status'] = determine_magic_status(team_wins, first_out_max_wins,
                                team_losses, last_in_max_losses, 0)

                playoff_stats = determine_magic_status(team_wins, first_out_max_wins, team_losses,
                                last_in_max_losses, magic_number_with_losses)

                final_team['status'] = playoff_stats[0]
                final_team['magic'] = playoff_stats[1]

            final_data[rank] = final_team
        results = [final_data, ranking, information]
        return results

    def determine_magic_status(team_wins, first_out_max_wins, team_losses, last_in_max_losses, magic_number_with_losses):
        """ This function determines the magic number and the playoff eligibility status for a team. """

        if team_wins > first_out_max_wins:
            status = 'IN'
            magic = '-'
        elif team_losses > last_in_max_losses:
            status = 'OUT'
            magic = '-'
        else:
            status = 'ALIVE'
            # Determines 'Magic Number' for teams to qualify
            magic = magic_number_with_losses - team_wins

        return([status, magic])

    def create_standings_message(number_of_teams, team_order):
        """ This function takes in the order of the teams and creates the message to send the users. """
        message = []
        for rank in range(number_of_teams):
            # add Rank
            message.append(str(rank+1))
            message.append(". ")
            message.append(team_order[rank])
            if (rank+1) != number_of_teams:
                message.append('\n')
        rankings_message = ''.join(message)
        return rankings_message

    def games_behind(leader_differential, team_wins, team_losses):
        """ This function takes in a team's wins & losses and the leader's differential and determines the team's games behind. """
        games_behind_leader = (leader_differential - (team_wins - team_losses)) / 2.0
        if games_behind_leader == 0:
            games_behind_leader = '-'
        return games_behind_leader

    returned_data = collect_ranking_data(teams)
    returned_ranking_data = returned_data[0]
    returned_differentials = returned_data[1]
    returned_winsall = returned_data[2]
    returned_lossesall = returned_data[3]

    order_results = order_rankings(teams, returned_ranking_data, returned_differentials)
    team_names_ranked = order_results[0]
    numbered_ranks = order_results[1]
    message = create_standings_message(number_of_teams, team_names_ranked)

    number_of_qualifiers = League.query.filter_by(league_name=league_name).first().number_of_qualifiers
    final_stats = determine_ranking_statistics(number_of_qualifiers, team_names_ranked,
                                               returned_ranking_data, number_of_teams,
                                               returned_winsall, returned_lossesall,
                                               numbered_ranks)
    final_stats_data = final_stats[0]
    final_information = final_stats[2]

    title = league_name + " Rankings"

    admin_leagues, user_leagues = admin_and_user_leagues(current_user.username)

    return render_template('home/rankings/rankings.html', ranking=numbered_ranks,
                           user_leagues=user_leagues, admin_leagues=admin_leagues,
                           league_name=league_name, admin_status=admin_status, number_of_teams=number_of_teams,
                           teams=teams, data=final_stats_data, information=final_information,
                           rankings_message=message, title=title)

def playoff_information(qualifiers, games, number_of_registered_teams, total_teams):
    """ This function determines if enough details have been entered to determine playoff information for a league. """
    if qualifiers is None or games is None or total_teams is None:
        return False
    if number_of_registered_teams != total_teams:
        return False
    return True

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

    # for every user in the updates for the league, if their phone number is
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
