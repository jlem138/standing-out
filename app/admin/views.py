# app/admin/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import admin
from .. import db
from forms import TeamForm, EventForm, LeagueForm, UserForm, RankingForm
from ..models import Team, Event, League, User, Ranking
from sqlalchemy import func, distinct

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

# team Views

@admin.route('/teams/<league>', methods=['GET', 'POST'])
@login_required
def list_teams(league):
    """
    List all teams
    """
    check_admin()
    teams = Team.query.all()

    return render_template('admin/teams/teams.html',
                           teams=teams, league=league, title="teams")



@admin.route('/teams/add', methods=['GET', 'POST'])
@login_required
def add_team():
    """
    Add a team to the database
    """
    check_admin()

    add_team = True

    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data,
                    division_name = form.division_name.data,
                    conference_name = form.conference_name.data,
                    league_name = form.league_name.data)
        try:
            # add team to the database
            db.session.add(team)
            db.session.commit()
            flash('You have successfully added a new team.')
        except:
            # in case team name already exists
            flash('Error: team name already exists.')

        # redirect to teams page
        return redirect(url_for('admin.list_teams'))

    # load team template
    return render_template('admin/teams/team.html', action="Add",
                           add_team=add_team, form=form,
                           title="Add Team")

@admin.route('/teams/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit_team(name):
    """
    Edit a team
    """
    check_admin()

    add_team = False

    team = Team.query.get_or_404(name)
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.division_name = form.division_name.data
        team.conference_name = form.conference_name.data
        team.league_name = form.league_name.data
        db.session.commit()
        flash('You have successfully edited the team.')

        # redirect to the teams page
        return redirect(url_for('admin.list_teams'))

    form.name.data = team.name
    form.division_name.data = team.division_name
    form.conference_name.data = team.conference_name
    form.league_name.data = team.league_name
    return render_template('admin/teams/team.html', action="Edit",
                           add_team=add_team, form=form,
                           team=team, title="Edit Team")


@admin.route('/teams/delete/<name>', methods=['GET', 'POST'])
@login_required
def delete_team(name):
    """
    Delete a team from the database
    """
    check_admin()

    team = Team.query.get_or_404(name)
    db.session.delete(team)
    db.session.commit()
    flash('You have successfully deleted the team.')

    # redirect to the teams page
    return redirect(url_for('admin.list_teams'))

    return render_template(title="Delete Team")


@admin.route('/events')
@login_required
def list_events():
    check_admin()
    """
    List all events
    """
    events = Event.query.all()
    return render_template('admin/events/events.html',
                           events=events, title='Events')

@admin.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    """
    Add a event to the database
    """
    check_admin()

    add_event = True

    form = EventForm()
    if form.validate_on_submit():
        event = Event(
        #id = form.id.data,
            day = form.day.data,
            winner = form.winner.data,
            loser = form.loser.data,
            winning_score = form.winning_score.data,
            losing_score = form.losing_score.data)

        try:
            # add event to the database
            db.session.add(event)
            db.session.commit()
            flash('You have successfully added a new event.')
        except:
            # in case event name already exists
            flash('Error: event name already exists.')

        # redirect to the events page
        return redirect(url_for('admin.list_events'))

    # load event template
    return render_template('admin/events/event.html', add_event=add_event, form=form, title='Add Event')

@admin.route('/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    """
    Edit a event
    """
    check_admin()

    add_event = False

    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        #event.id = form.id.data
        event.day = form.day.data
        event.winner = form.winner.data
        event.loser = form.loser.data
        event.winning_score = form.winning_score.data
        event.losing_score = form.losing_score.data
        db.session.commit()
        flash('You have successfully edited the event.')

        # redirect to the events page
        return redirect(url_for('admin.list_events'))

    #form.id.data = event.id
    form.day.data = event.day
    form.winner.data = event.winner
    form.loser.data = event.loser
    form.winning_score.data = event.winning_score
    form.losing_score.data = event.losing_score

    return render_template('admin/events/event.html', action="Edit",
                           add_event=add_event, form=form,
                           event=event, title="Edit EventX")


@admin.route('/events/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    """
    Delete a event from the database
    """
    check_admin()

    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('You have successfully deleted the event.')

    # redirect to the events page
    return redirect(url_for('admin.list_events'))

    return render_template(title="Delete Event")

@admin.route('/leagues/add', methods=['GET', 'POST'])
@login_required
def add_league():
    """
    Add a team to the database
    """
    check_admin()

    add_league = True

    form = LeagueForm()
    if form.validate_on_submit():
        league = League(
                    name = form.name.data,
                    number_of_conferences=form.number_of_conferences.data,
                    number_of_total_teams = form.number_of_total_teams.data,
                    number_of_rounds = form.number_of_rounds.data,
                    number_of_qualifiers = form.number_of_qualifiers.data,
                    is_byes = form.is_byes.data
                    )

        try:
            # add team to the database
            db.session.add(league)
            db.session.commit()
            flash('You have successfully added a new league.')
        except:
            # in case team name already exists
            flash('Error: league already exists.')

        # redirect to teams page
        return redirect(url_for('admin.list_leagues'))

    # load team template
    return render_template('admin/leagues/league.html', action="Add",
                           add_league=add_league, form=form,
                           title="Addx League")


@admin.route('/leagues', methods=['GET', 'POST'])
@login_required
def list_leagues():
    """
    List all leagues
    """
    check_admin()

    leagues = League.query.all()

    return render_template('admin/leagues/leagues.html',
                           leagues=leagues, title="leagues")




@admin.route('/leagues/delete/<name>', methods=['GET', 'POST'])
@login_required
def delete_league(name):
    """
    Delete a league from the database
    """
    check_admin()

    league = League.query.get_or_404(name)
    db.session.delete(league)
    db.session.commit()
    flash('You have successfully deleted the league.')

    # redirect to the events page
    return redirect(url_for('admin.list_leagues'))

    return render_template(title="Delete Leagues")


@admin.route('/leagues/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit_league(name):
    """
    Edit a league
    """
    check_admin()

    add_league = False

    league = League.query.get_or_404(name)
    form = LeagueForm(obj=league)
    if form.validate_on_submit():
        league.name = form.name.data
        league.number_of_conferences = form.number_of_conferences.data
        league.number_of_games = form.number_of_games.data
        league.number_of_total_teams = form.number_of_total_teams.data
        league.number_of_rounds = form.number_of_rounds.data
        league.number_of_qualifiers = form.number_of_qualifiers.data
        league.is_byes = form.is_byes.data
        db.session.commit()
        flash('You have successfully edited the league.')

        # redirect to the events page
        return redirect(url_for('admin.list_leagues'))

    form.name.data = league.name
    form.number_of_conferences.data = league.number_of_conferences
    form.number_of_games.data = league.number_of_games
    form.number_of_total_teams.data = league.number_of_total_teams
    form.number_of_rounds.data = league.number_of_rounds
    form.number_of_qualifiers.data = league.number_of_qualifiers
    form.is_byes.data = league.is_byes

    return render_template('admin/leagues/league.html', action="Edit",
                           add_league=add_league, form=form,
                           league=league, title="Edit League")


@admin.route('/rankings/<leaguename>', methods=['GET', 'POST'])
@login_required
def list_rankings(leaguename):
    """
    List all teams
    """
    check_admin()

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
        team_data['percentage'] = wins / (wins + losses)
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


    final_data = {}
    for rank in range(number_of_teams):
        final_team = {}
        name = differentials[rank]
        team_wins = ranking_data[name]['wins']
        team_losses = ranking_data[name]['losses']
        final_team['place'] = rank + 1
        final_team['name'] = name
        final_team['wins'] = team_wins
        final_team['losses'] = team_losses
        final_team['GB'] = (leader_differential - (team_wins - team_losses)) / 2.0
        magic_number = (games + 1) - (last_in_losses + team_wins)
        final_team['magic'] = magic_number
        if (games - team_wins < first_out_least_possible_losses):
            playoff_marker = 'IN'
        elif (games - team_losses < last_in_least_possible_wins):
            playoff_marker = 'OUT'
        else:
            playoff_marker = 'ALIVE'
        final_team['eligible'] = playoff_marker
        final_data[rank] = final_team;

    return render_template('admin/rankings/rankings.html', ranking=ranking,
                           teams=teams,data=final_data, diffs=differentials,title=leaguename)


@admin.route('/users')
@login_required
def list_users():
    """
    List all users
    """
    check_admin()

    users = User.query.all()
    return render_template('admin/users/users.html',
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
