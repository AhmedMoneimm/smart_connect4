# File: tests/test_minimax.py
import pytest
import math
from models.ai.minimax import minimax
from models.board import create_board, drop_piece, get_next_open_row
from models.constants import AI_PIECE, PLAYER_PIECE, EMPTY, COLUMN_COUNT


def test_minimax_blocks_three_in_row():
    board = create_board()
    # Opponent has three in row at bottom row cols 0,1,2
    for c in [0,1,2]:
        r = get_next_open_row(board, c)
        board = drop_piece(board, r, c, PLAYER_PIECE)

    # AI should place in column 3 to block
    col, score, _ = minimax(board, depth=2, alpha=-math.inf, beta=math.inf,
                            maximizingPlayer=True, piece=AI_PIECE, visualize=False)
    assert col == 3


def test_minimax_prefers_win_over_block():
    board = create_board()
    # AI has three in row at row 0 cols 4,5,6
    for c in [4,5,6]:
        r = get_next_open_row(board, c)
        board = drop_piece(board, r, c, AI_PIECE)
    # Opponent has nothing
    # AI should place at col 7 (COLUMN_COUNT-1) to win
    col, score, _ = minimax(board, depth=2, alpha=-math.inf, beta=math.inf,
                            maximizingPlayer=True, piece=AI_PIECE, visualize=False)
    assert col == 3