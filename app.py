from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import json
import os
import datetime
import requests

app = Flask(__name__)
app.config['MAIL_SERVER'] = "smtp.sendgrid.net"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "NBA Bot"
app.config['MAIL_PASSWORD'] = os.environ.get("API_KEY")
app.config['MAIL_USE_TLS'] = True
app.config["MAIL_DEFAULT_SENDER"] = "nbagametracker@gmail.com"
mail = Mail(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
db = SQLAlchemy(app)

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(120))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route('/')
def main_page():
    games = get_current_games()
    return render_template("index.html", games=games)


def get_current_games():
    scoreboard_data = get_data()['scoreboard']
    current_games = scoreboard_data.get("games", [])
    all_games = []
    for game in current_games:
        game_info = {
            "HOME": game['homeTeam'],
            "AWAY": game['awayTeam'],
            "time_remaining": game['gameStatusText'].split(' ')[1],
            "quarter": game['period'],
            "ID": game['gameId']
        }
        all_games.append(game_info)
    return all_games


def get_data():
    r = requests.get(SCOREBOARD_URL)
    return r.json()


@app.route('/email', methods=["GET", "POST"])
def send_emails():
    if request.method == "POST":
        new_mail = request.form["email"]
        if User.query.filter_by(email=new_mail).first():
            print("User is already in the database")
        else:
            name = request.form["name"]
            new_user = User(name, new_mail)
            db.session.add(new_user)
            db.session.commit()
        msg = Message(
            subject="Today's NBA Game Scores",
            sender="nbagametracker@gmail.com",
            recipients=[r.email for r in User.query.filter_by(email=new_mail)]
        )
        msg.body = render_template("index.html", games=get_current_games())
        cur_time = datetime.datetime.now()
        cur_time = cur_time.replace(hour=8, minute=1)
        unix_time = datetime.datetime.timestamp(cur_time)
        msg.extra_headers = {"X-SMTPAPI": json.dumps({'send_at': unix_time})}
        mail.send(msg)
        return "Sending Email"
    return render_template("email.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(threaded=True, debug=True)
