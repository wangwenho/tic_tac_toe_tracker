from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import datetime

# initialize the web app and the database

app = Flask(__name__)
client = MongoClient(host="localhost", port=27017)
db = client.tic_tac_toe

# innitialize the game board and the players

# use list to represent the board
board = ['' for _ in range(9)]
player_1 = ''
player_2 = ''
current_player = 'O'

# noted that we use 1 to 9 to represent the position, which is more human readable
# | 1 | 2 | 3 |
# | 4 | 5 | 6 |
# | 7 | 8 | 9 |
winning_combinations = [{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {1, 4, 7}, {2, 5, 8}, {3, 6, 9}, {1, 5, 9}, {3, 5, 7}]
player_1_moves = set()
player_2_moves = set()
moves_sequence = []

# functions

# get the current game state
def get_game_state():
    for combination in winning_combinations:
        if combination.issubset(player_1_moves):
            print('Player 1 wins')
            return 1, combination
        if combination.issubset(player_2_moves):
            print('Player 2 wins')
            return 2, combination
    if len(player_1_moves) + len(player_2_moves) == 9:
        print('Tie')
        return 3, None
    return 0, None

# reset the game board
def reset_game():
    global board, current_player, player_1_moves, player_2_moves, moves_sequence
    board = ['' for _ in range(9)]
    current_player = 'O'
    player_1_moves = set()
    player_2_moves = set()
    moves_sequence = []

# update stats of the players
def update_player_stats(player, wins=0, losses=0, ties=0):
    if db.players.find_one({'player': player}):
        db.players.update_one({'player': player}, {'$inc': {'total_games': 1, 'wins': wins, 'losses': losses, 'ties': ties}})
    else:
        db.players.insert_one({
            'player': player,
            'total_games': 1,
            'wins': wins,
            'losses': losses,
            'ties': ties
        })

# insert the game history into the database
def insert_game_history(is_tie, winner, loser):
    db.history.insert_one({
        'match_timestamp': datetime.datetime.now(),
        'player_1': player_1,
        'player_2': player_2,
        'is_tie': is_tie,
        'winner': winner,
        'loser': loser,
        'player_1_moves': list(player_1_moves),
        'player_2_moves': list(player_2_moves),
        'total_moves': len(moves_sequence),
        **{f'move_{i+1}': moves_sequence[i] if i < len(moves_sequence) else None for i in range(9)}
    })

# web routes

@app.route('/')
def index():
    return redirect(url_for('welcome'))

# welcome page
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        return redirect(url_for('enter_player_name'))
    return render_template('welcome.html')

# route for entering the player names
@app.route('/username', methods=['GET', 'POST'])
def enter_player_name():
    global player_1, player_2
    if request.method == 'POST':
        if 'player_1' in request.form and 'player_2' in request.form:
            player_1 = request.form['player_1']
            player_2 = request.form['player_2']
            print(player_1, player_2)
            print('Game started')
            return redirect(url_for('play_game'))
    return render_template('username.html')

# we use the same route for playing the game and displaying the game board
@app.route('/game', methods=['GET', 'POST'])
def play_game():
    global board, player_1, player_2, current_player, player_1_moves, player_2_moves, moves_sequence

    # check the game state
    state, winning_combination = get_game_state()
    if state == 1:
        update_player_stats(player_1, wins=1)
        update_player_stats(player_2, losses=1)
        insert_game_history(is_tie=False, winner=player_1, loser=player_2)
        reset_game()
        return redirect(url_for('play_game'))
    
    elif state == 2:
        update_player_stats(player_2, wins=1)
        update_player_stats(player_1, losses=1)
        insert_game_history(is_tie=False, winner=player_2, loser=player_1)
        reset_game()
        return redirect(url_for('play_game'))
    
    elif state == 3:
        update_player_stats(player_1, ties=1)
        update_player_stats(player_2, ties=1)
        insert_game_history(is_tie=True, winner=None, loser=None)
        reset_game()
        return redirect(url_for('play_game'))
    
    if request.method == 'POST':

        # turnover the game
        if 'turnover' in request.form:
            player_1, player_2 = player_2, player_1
            reset_game()
            return redirect(url_for('play_game'))
        
        # handle the player's move
        index = int(request.form['index'])
        if board[index] == '':
            moves_sequence.append(index + 1)

            if current_player == 'O':
                player_1_moves.add(index + 1)
            else:
                player_2_moves.add(index + 1)

            board[index] = current_player
            state, winning_combination = get_game_state()
            current_player = 'X' if current_player == 'O' else 'O'
            return render_template('board.html', board=board, player_1=player_1, player_2=player_2, current_player=current_player, state=state, winning_combination=winning_combination)
    
    return render_template('board.html', board=board, player_1=player_1, player_2=player_2, current_player=current_player, state=state)

# show the game history
@app.route('/history')
def show_history():
    history = db.history.find()
    return render_template('history.html', history=history)

# show the players statistics
@app.route('/stats')
def show_stats():
    players = db.players.find()
    return render_template('stats.html', players=players)

if __name__ == '__main__':
    app.run(debug=True)