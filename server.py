from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# Database Models
class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.now)
    teams = db.relationship('Team', backref='season', lazy=True)
    games = db.relationship('Game', backref='season', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    players = db.relationship('Player', backref='team', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    stats = db.relationship('Stat', backref='player', lazy=True)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    score_team1 = db.Column(db.Integer, default=0)
    score_team2 = db.Column(db.Integer, default=0)
    stats = db.relationship('Stat', backref='game', lazy=True)

class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    rebounds = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

# Routes
@app.route('/')
def home():
    seasons = Season.query.all()
    current_season = Season.query.order_by(Season.start_date.desc()).first()
    return render_template('home.html', seasons=seasons, current_season=current_season)

@app.route('/current-season')
def current_season():
    current_season = Season.query.order_by(Season.start_date.desc()).first()
    return render_template('current_season.html', season=current_season)

@app.route('/add-season', methods=['GET', 'POST'])
def add_season():
    if request.method == 'POST':
        season_name = request.form['season_name']
        new_season = Season(name=season_name)
        db.session.add(new_season)
        db.session.commit()
        flash('New season added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_season.html')

@app.route('/archive')
def archive():
    seasons = Season.query.order_by(Season.start_date.desc()).all()
    return render_template('archive.html', seasons=seasons)

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        team1_id = request.form['team1']
        team2_id = request.form['team2']
        score_team1 = request.form['score_team1']
        score_team2 = request.form['score_team2']
        game = Game(team1_id=team1_id, team2_id=team2_id, score_team1=score_team1, score_team2=score_team2)
        db.session.add(game)
        db.session.commit()
        flash('Game stats updated successfully!', 'success')
        return redirect(url_for('home'))
    
    current_season = Season.query.order_by(Season.start_date.desc()).first()
    teams = Team.query.filter_by(season_id=current_season.id).all()
    return render_template('game.html', teams=teams)

@app.route('/player/<int:player_id>')
def player(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player.html', player=player)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

