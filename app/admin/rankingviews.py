# app/admin/views.py

from flask import abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required

from . import admin
from .. import db
from .forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm, UpdateForm
from ..models import Team, Event, League, User, Ranking, Update
from sqlalchemy import func, distinct, MetaData, engine, Table, create_engine, select
from .database import database_engine

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)


@admin.route('/rankings/<leaguename>', methods=['GET', 'POST'])
@login_required
def list_rankings(leaguename):
    """
    List all teams
    """
    #check_admin()

    engine = database_engine
    conn = engine.connect()
    #current_information = Current(league_name="MLB", user_id = 4)
    #db.session.add(current_information)
    #db.session.commit()
    # Enter "current league" in Current table
    #res = conn.execute("insert into currents (league_name, user_id) values ('MLB', 2)");
    # ins = currents.insert()
    # conn.execute(ins, league_name="MLB", user_id = 4);
    # res = conn.execute("select * from currents")
    # for row in res:
    #     print("ROW", row)

    #meta = MetaData(engine, reflect=True)
    #table = meta.tables['leagues']
    #select_st = select([table]).where(table.c.name == "WNBA")
    #res = conn.execute("select * from events where winner = 'Seattle Storm'")
    #for row in res:
    #    print(row)

    #wnbaleague = "WNBA"
    #league = wnbaleague

    games = League.query.filter_by(name=leaguename).first().number_of_games
    number_of_teams = League.query.filter_by(name=leaguename).first().number_of_total_teams
    qualifiers = League.query.filter_by(name=leaguename).first().number_of_qualifiers

    teams = Team.query.filter_by(league_name=leaguename)
    results = Event.query.all()

    def get_count(q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count_x = q.session.execute(count_q).scalar()
        return count_x

    ranking_data = {}
    differentials = []
    winsall = []
    lossesall = []
    ranking = {}
    place = 0
    for team in teams:
        team_data = {}
        wins = get_count(Event.query.filter_by(winner=team.name))
        losses = get_count(Event.query.filter_by(loser=team.name))
        team_data['wins'] = wins
        team_data['losses'] = losses
        wonloss = wins - losses
        team_data['differential'] = wonloss
        differentials.append(wonloss)
        winsall.append(wins)
        lossesall.append(losses)
        ranking_data[team.name] = team_data

    differentials.sort(reverse=True)
    winsall.sort(reverse=True)
    lossesall.sort(reverse=True)

    not_stored = True
    for team in teams:
        team_diff = ranking_data[team.name]['differential']
        not_stored = True
        for j in range(number_of_teams):
            current_diff = differentials[j]
            if (current_diff == team_diff) and (not_stored == True):
                differentials[j] = team.name
                ranking[j] = j
                not_stored = False
                print(j, team.name, current_diff, team_diff)

    last_in = differentials[qualifiers]
    last_in_wins = ranking_data[last_in]['wins']
    last_in_losses = ranking_data[last_in]['losses']
    leader_differential = ranking_data[differentials[0]]['differential']

    first_out_least_possible_losses = lossesall[number_of_teams - qualifiers - 1]
    last_in_least_possible_wins = winsall[qualifiers]

    def zero_out(entry):
        if (type(entry) != int):
            return 0;
        else:
            return entry;

    # If including win percentage, account for a team that hasn't played yet (division by 0)
    final_data = {}
    for rank in range(number_of_teams):
        final_team = {}
        name = differentials[rank]
        team_wins = (ranking_data[name]['wins'])
        team_losses = (ranking_data[name]['losses'])
        final_team['place'] = rank + 1
        final_team['name'] = name
        final_team['wins'] = team_wins
        final_team['losses'] = team_losses
        final_team['GB'] = (leader_differential - (team_wins - team_losses)) / 2.0
        magic_number = (games + 1) - (last_in_losses + team_wins) + 1
        final_team['magic'] = magic_number
        if (games - team_wins < first_out_least_possible_losses):
            playoff_marker = 'IN'
        elif (games - team_losses < last_in_least_possible_wins):
            playoff_marker = 'OUT'
        else:
            playoff_marker = 'ALIVE'
        final_team['eligible'] = playoff_marker
        final_data[rank] = final_team;

    print("FD",final_data)
    print("ranking", ranking)

    return render_template('admin/rankings/rankings.html', ranking=ranking, leaguename=leaguename,
                           teams=teams,data=final_data, diffs=differentials,title=leaguename)
