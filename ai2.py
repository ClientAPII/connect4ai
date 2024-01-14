import copy
import math
from helper import *


def ai(arr, player):
    """
    :param arr: current status of the board as type list[list[int]].
    The integers can either be 0 (cell empty), 1 (token of player 1) or 2 (token of player 2).
    :param player: Integer which is either 1 (turn of player 1) or 2 (turn of player 2).
    :return: Integer between 0 and 6 indicating in which row the next token shall be placed.

    Write your own AI in this function, do not change the function signature.
    Feel free to use any of the constants/methods in the helper.py / config.py file.
    You can/shall also override the ai() function in ai2.py to let
    different versions of you AI compete against each other.
    """

    # insert token into random row
    while True:
        col = random.randint(0, N_COLS-1)
        if not column_is_full(arr, col):
            return col





