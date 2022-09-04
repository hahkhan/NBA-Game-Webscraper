from flask import Flask,render_template,request
from flask_mail import Mail, Message
from flask_sqlalchemy import sqlalchemy

import json
import os
import datetime
import requests
app = Flask(__name__)
URL = "https://data.nba.net"
@app.route('/')
def main_page():
    games = get_current_games()
    return render_template("index.html", games = games)


def get_current_games():
    scoreboard_data = get_data()['currentScoreboard']
    current_games = requests.get('https://data.nba.net/prod/v1/20220130/scoreboard.json').json()['games']
    all_games = []
    for game in current_games:
        game_info ={"HOME": game['hTeam'],"AWAY": game['vTeam'],"time_remaining": game['clock'],"quarter": game['period'], "ID": game['gameId']}
        all_games.append(game_info)
    return all_games


def get_data():
    r = requests.get('https://data.nba.net/prod/v1/today.json')
    return r.json()['links']

@app.route('/email', methods = ["GET", "POST"])
def send_emails():
    if request.method =="POST":
        
        return "Sending Email"
    return render_template("email.html")

if __name__ == "__main__":
    app.run(threaded = True, debug = True)