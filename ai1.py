import copy
import math
import random
import logging
from helper import *

# Bevor sie loggen wollen, ändern sie die color codes in config.py zu folgendem:
#GREY = ''
#BLUE = ''
#YELLOW = ''
#RED = ''

LOG_TO_FILE = False

transposition_table = {}

# Configure the logger based on the flag
if LOG_TO_FILE:
    logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(message)s')
else:
    pass

# Constants
EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2
WINDOW_LENGTH = 4

def score_position(board, piece):
    score = 0
    opponent_piece = PLAYER_1 if piece == PLAYER_2 else PLAYER_2

    # Center column preference
    center_array = [int(i[N_COLS//2]) for i in board]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Offensive and defensive scoring
    for window in get_all_windows(board):
        if window.count(piece) == 4:
            score += 1000
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 100
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 50

        # Potential winning position
        if window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 5

        # Threat
        if window.count(opponent_piece) == 3 and window.count(EMPTY) == 1:
            score -= 80

    # Favor certain rows based on the player
    favored_rows = [0, 2, 4, 6] if piece == PLAYER_1 else [1, 3, 5, 7]
    for row in favored_rows:
        if row < len(board):
            score += board[row].count(piece)

    return score

def get_all_windows(board): #Alle Spielmöglichkeiten
    windows = []

    # Horizontal windows
    for row in range(N_ROWS):
        for col in range(N_COLS - 3):
            windows.append(board[row][col:col+WINDOW_LENGTH])

    # Vertical windows
    for row in range(N_ROWS - 3):
        for col in range(N_COLS):
            windows.append([board[row+i][col] for i in range(WINDOW_LENGTH)])

    # Positive diagonal windows
    for row in range(N_ROWS - 3):
        for col in range(N_COLS - 3):
            windows.append([board[row+i][col+i] for i in range(WINDOW_LENGTH)])

    # Negative diagonal windows
    for row in range(3, N_ROWS):
        for col in range(N_COLS - 3):
            windows.append([board[row-i][col+i] for i in range(WINDOW_LENGTH)])

    return windows

def get_next_open_row(board, col): #Gibt die nächste freie Reihe zurück
    for r in range(N_ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1

def winning_move(board, piece): #Gibt True zurück, wenn ein Spieler gewonnen hat
    for c in range(N_COLS-3):
        for r in range(N_ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    for c in range(N_COLS):
        for r in range(N_ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    for c in range(N_COLS-3):
        for r in range(N_ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    for c in range(N_COLS-3):
        for r in range(3, N_ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False

def get_valid_locations(board): #Gibt alle gültigen Züge an, welche ein Spieler machen kann
    valid_locations = []
    for col in range(N_COLS):
        if not column_is_full(board, col):
            valid_locations.append(col)

    # Sort the valid moves based on their distance from the center column
    valid_locations.sort(key=lambda x: abs(x - N_COLS // 2))

    return valid_locations

def is_terminal_node(board): # Hat ein Spieler gewonnen?
    return winning_move(board, PLAYER_1) or winning_move(board, PLAYER_2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    # Here is where the magic happens, Minimax Algorithmus it Alpha-Beta Pruning
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    # Convert the board to a tuple so it can be used as a dictionary key
    board_tuple = tuple(map(tuple, board))

    # Check if the board state is in the transposition table
    if board_tuple in transposition_table:
        return transposition_table[board_tuple]

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_2):
                return (None, 10000000000000)
            elif winning_move(board, PLAYER_1):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, PLAYER_2))

    # Sort the valid moves based on their scores
    scored_moves = [(col, score_position(board, PLAYER_2 if maximizingPlayer else PLAYER_1)) for col in valid_locations]
    scored_moves.sort(key=lambda x: -x[1] if maximizingPlayer else x[1])

    if maximizingPlayer:
        value = -math.inf
        column = scored_moves[0][0]
        for col, _ in scored_moves:
            row = get_next_open_row(board, col)
            b_copy = copy.deepcopy(board)
            place_token(b_copy, col, PLAYER_2)
            if winning_move(b_copy, PLAYER_2):
                return (col, 10000000000000)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        # Store the result in the transposition table
        transposition_table[board_tuple] = (column, value)
        return column, value

    else:
        value = math.inf
        column = scored_moves[0][0]
        for col, _ in scored_moves:
            row = get_next_open_row(board, col)
            b_copy = copy.deepcopy(board)
            place_token(b_copy, col, PLAYER_1)
            if winning_move(b_copy, PLAYER_1):
                return (col, -10000000000000)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        # Store the result in the transposition table
        transposition_table[board_tuple] = (column, value)
        return column, value

def ai(arr, player):
    depth = 8 # tiefe hier anpassbar
    col, minimax_score = minimax(arr, depth, -math.inf, math.inf, True)

    return col