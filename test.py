
# @app.route('/handle_action', methods=['POST'])
# def handle_action():
#     global board, current_player, player_1_moves, player_2_moves, moves_sequence
#     data = request.get_json()
#     game_data = db.history.find_one({"_id": ObjectId(data.get('id'))})
#     player_1 = game_data['player_1']
#     player_2 = game_data['player_2']
#     winner = game_data['winner']
#     for i in range(1, 10):
#         if game_data[f'move_{i}'] == None:
#             break
#         moves_sequence.append(game_data[f'move_{i}'])
#     return render_template('review.html', board=[], player_1=player_1, player_2=player_2)