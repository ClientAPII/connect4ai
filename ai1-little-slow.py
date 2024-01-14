import copy
import math
import random
from helper import *


# Constants
EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2
WINDOW_LENGTH = 4

transposition_table = {}

def score_position(board, piece):
    score = 0
    # Score center column
    center_array = [int(i[N_COLS//2]) for i in board]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for row in range(N_ROWS):
        row_array = [int(i) for i in board[row]]
        for c in range(N_COLS-3):
            window = row_array[c:c+WINDOW_LENGTH]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(EMPTY) == 1:
                score += 5
            elif window.count(piece) == 2 and window.count(EMPTY) == 2:
                score += 2

    # Score vertical
    for col in range(N_COLS):
        col_array = [int(board[row][col]) for row in range(N_ROWS)]
        for r in range(N_ROWS-3):
            window = col_array[r:r+WINDOW_LENGTH]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(EMPTY) == 1:
                score += 5
            elif window.count(piece) == 2 and window.count(EMPTY) == 2:
                score += 2

    # Score positive sloped diagonal
    for r in range(N_ROWS-3):
        for c in range(N_COLS-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(EMPTY) == 1:
                score += 5
            elif window.count(piece) == 2 and window.count(EMPTY) == 2:
                score += 2

    # Score negative sloped diagonal
    for r in range(N_ROWS-3, N_ROWS):
        for c in range(N_COLS-3):
            window = [board[r-i][c+i] for i in range(WINDOW_LENGTH)]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(EMPTY) == 1:
                score += 5
            elif window.count(piece) == 2 and window.count(EMPTY) == 2:
                score += 2

    return score

def get_next_open_row(board, col):
    for r in range(N_ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(N_COLS-3):
        for r in range(N_ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(N_COLS):
        for r in range(N_ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(N_COLS-3):
        for r in range(N_ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(N_COLS-3):
        for r in range(3, N_ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False

def get_valid_locations(board):
    valid_locations = []
    for col in range(N_COLS):
        if not column_is_full(board, col):
            valid_locations.append(col)

    # Prioritize moves that complete or block a connection of four
    for col in valid_locations:
        if winning_move(board, col):
            valid_locations.remove(col)
            valid_locations.insert(0, col)

    # Prioritize moves in the center of the board
    valid_locations.sort(key=lambda x: abs(x - N_COLS // 2))

    return valid_locations

def is_terminal_node(board):
    return winning_move(board, PLAYER_1) or winning_move(board, PLAYER_2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    # Convert board to a hashable type to use it as a key in the transposition table
    board_tuple = tuple(map(tuple, board))

    # Check if the current state is in the transposition table
    if (board_tuple, depth, maximizingPlayer) in transposition_table:
        return transposition_table[(board_tuple, depth, maximizingPlayer)]

    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_2):
                return (None, 10000000000000)
            elif winning_move(board, PLAYER_1):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, PLAYER_2))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy.deepcopy(board)
            place_token(b_copy, col, PLAYER_2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy.deepcopy(board)
            place_token(b_copy, col, PLAYER_1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break

    # Store the result in the transposition table
    transposition_table[(board_tuple, depth, maximizingPlayer)] = (column, value)

    return column, value

def ai(arr, player):
    # Iterative deepening
    for depth in range(1, 7):  # Adjust the range based on the performance of your AI
        col, minimax_score = minimax(arr, depth, -math.inf, math.inf, True)
        if minimax_score >= 10000000000000:  # Found a winning move
            break

    return col