import pymysql
import pymysql.cursors
import os
import subprocess
from app.models import User
from app import db

db1 = pymysql.connect(
    host="localhost",
    user="sunlight",
    password="!f0e9Rd8r7ey^",
    db = "standings",
    cursorclass=pymysql.cursors.DictCursor
)

cursor = db1.cursor()

def add_quotes(item):
    string = "\"{0}\"".format(item)
    return(string)

def insert_update_query(username, first_name, last_name, league_name, is_admin):
    add_update = "insert into updates (username, first_name, last_name, league_name, is_admin) VALUES ( {0}, {1}, {2}, {3}, {4})".format(add_quotes(username), add_quotes(first_name), add_quotes(last_name), add_quotes(league_name), add_quotes(is_admin))
    # Insert new team
    try:
        cursor.execute(add_update)
        db1.commit()
        #    db.close()
    except Exception as e:
        print(e)

insert_update_query("jlem138", "Joshua", "Lemkin", "NBA", 1)
insert_update_query("jlem138", "Joshua", "Lemkin", "MLB", 1)
insert_update_query("john", "John", "Smith", "WNBA", 1)
