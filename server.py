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

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    players = db.relationship('Player', backref='team', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    games_played = db.Column(db.Integer, default=0)
    stats = db.relationship('Stat', backref='player', lazy=True)

class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    rebounds = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    steals = db.Column(db.Integer, default=0)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)

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
        team_names = request.form.getlist('team_name[]')
        password = request.form['password']
        
        # Password protection
        if password != 'admin123':
            flash('Incorrect password!', 'danger')
            return redirect(url_for('add_season'))
        
        # Create new season
        new_season = Season(name=season_name)
        db.session.add(new_season)
        db.session.commit()

        # Add teams and players
        for idx, team_name in enumerate(team_names):
            new_team = Team(name=team_name, season_id=new_season.id)
            db.session.add(new_team)
            db.session.commit()

            player_names = request.form.getlist(f'player_name_team_{idx}[]')
            for player_name in player_names:
                new_player = Player(name=player_name, team_id=new_team.id)
                db.session.add(new_player)

        db.session.commit()
        flash('New season and teams added successfully!', 'success')
        return redirect(url_for('home'))

    # Initialize teams and players_by_team for the form (in case there are no teams yet)
    teams = [(0, '')]  # One empty team for starting
    players_by_team = {0: ['']}  # One empty player for team 0
    
    return render_template('add_season.html', teams=teams, players_by_team=players_by_team)


@app.route('/archive')
def archive():
    seasons = Season.query.order_by(Season.start_date.desc()).all()
    return render_template('archive.html', seasons=seasons)

@app.route('/player/<int:player_id>')
def player(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player.html', player=player)

# Route for recording a game result
@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        team1_id = request.form['team1']
        team2_id = request.form['team2']
        score_team1 = int(request.form['score_team1'])
        score_team2 = int(request.form['score_team2'])

        # Find the teams
        team1 = Team.query.get(team1_id)
        team2 = Team.query.get(team2_id)

        # Determine winner and loser
        if score_team1 > score_team2:
            team1.wins += 1
            team2.losses += 1
        elif score_team2 > score_team1:
            team2.wins += 1
            team1.losses += 1
        else:
            flash('The game was a tie, no changes to wins/losses', 'info')

        db.session.commit()
        flash('Game result updated successfully!', 'success')
        return redirect(url_for('home'))

    current_season = Season.query.order_by(Season.start_date.desc()).first()
    teams = Team.query.filter_by(season_id=current_season.id).all()
    return render_template('game.html', teams=teams)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
