# tests.py

import unittest

from flask_testing import TestCase

from app import create_app, db
from app.models import User, League, Team, Event, Ranking, Update
from flask import abort, url_for

import os

class TestBase(TestCase):

    def create_app(self):

        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql://ranktestuser:ranktestpass@localhost/rankstest'
        )
        return app

    def setUp(self):
        """
        Will be called before every test
        """

        db.create_all()

        leaguewnba = League(name="WNBA", number_of_games=34, number_of_conferences= 1, number_of_total_teams=12, number_of_rounds=4, number_of_qualifiers=8, is_byes=True)

        leaguemlb = League(name="MLB", number_of_games=162, number_of_conferences= 1, number_of_total_teams=162, number_of_rounds=4, number_of_qualifiers=10, is_byes=True)

        db.session.add(leaguewnba)
        db.session.add(leaguemlb)
        db.session.commit()

        # create test admin user
        admin = User(username="admin", password="adminpass", is_admin=True, league_name="WNBA")

        # create test non-admin user
        user = User(username="test_user", password="testpass", league_name="WNBA")

        # save users to database
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

        chicago_sky = Team(name="Chicago Sky", division_name="None",  conference_name="East", league_name="WNBA")
        dallas_wings = Team(name="Dallas Wings", division_name="None",  conference_name="West", league_name="WNBA")

        db.session.add(chicago_sky)
        db.session.add(dallas_wings)
        db.session.commit()


    def tearDown(self):
        """
        Will be called after every test
        """

        db.session.remove()
        db.drop_all()


class TestModels(TestBase):

    def test_user_model(self):
        """
        Test number of records in Users table
        """
        self.assertEqual(User.query.count(), 2)

    def test_league_model(self):
        """
        Test number of records in Users table
        """
        self.assertEqual(League.query.count(), 2)

    def test_team_model(self):
        """
        Test number of records in Department table
        """

        # create test teams
        #chicago_sky = Team(name="Chicago Sky", division_name="None",  conference_name="East", league_name="WNBA")

        #dallas_wings = Team(name="Dallas Wings", division_name="None",  conference_name="West", league_name="WNBA")

        # save two teams to database
        #db.session.add(chicago_sky)
        #db.session.add(dallas_wings)
        #db.session.commit()

        self.assertEqual(Team.query.count(), 2)


    def test_event_model(self):
        """
        Test number of records in Department table
        """

        # create test game result

        # save department to database
        #db.session.add(game_result)
        #db.session.commit()

        game_result = Event(day="2009-12-12", winner = "Dallas Wings", loser = "Dallas Wings", league_name = "WNBA", winning_score = 84, losing_score=73)

        db.session.add(game_result)
        db.session.commit()


        self.assertEqual(Event.query.count(), 1)


    def test_ranking_model(self):
        """
        Test number of records in Role table
        """

        # create test role
        ranking1 = Ranking(team="Chicago Sky")
        ranking2 = Ranking(team="Dallas Wings")

        # save role to database
        db.session.add(ranking1)
        db.session.add(ranking2)
        db.session.commit()

        self.assertEqual(Ranking.query.count(), 2)

    def test_update_model(self):
        """
        Test number of records in Role table
        """

        # create test role
        update = Update(username="test_user", league_name="MLB")

        # save role to database
        db.session.add(update)
        db.session.commit()

        self.assertEqual(Update.query.count(), 1)


    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('home.homepage'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
