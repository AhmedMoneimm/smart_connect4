# File: tests/test_board.py
import pytest
from models.board import (
    create_board, drop_piece, is_valid_location, get_valid_locations,
    get_next_open_row, winning_move, generate_windows, score_position
)
from models.constants import EMPTY, PLAYER_PIECE, AI_PIECE, ROW_COUNT, COLUMN_COUNT, WINDOW_LENGTH


def test_create_and_drop_piece():
    board = create_board()
    assert board.count(EMPTY) == ROW_COUNT * COLUMN_COUNT

    # Drop a piece into column 3
    row = get_next_open_row(board, 3)
    new_board = drop_piece(board, row, 3, AI_PIECE)
    assert new_board[row * COLUMN_COUNT + 3] == AI_PIECE
    assert board != new_board


def test_valid_locations_and_next_row():
    board = create_board()
    # All columns valid initially
    valid = get_valid_locations(board)
    assert set(valid) == set(range(COLUMN_COUNT))

    # Fill column 0
    for _ in range(ROW_COUNT):
        row = get_next_open_row(board, 0)
        board = drop_piece(board, row, 0, PLAYER_PIECE)
    assert 0 not in get_valid_locations(board)
    assert not is_valid_location(board, 0)


def test_winning_move_horizontal():
    board = create_board()
    # Place 4 in a row for AI_PIECE at bottom row
    for col in range(4):
        row = get_next_open_row(board, col)
        board = drop_piece(board, row, col, AI_PIECE)
    assert winning_move(board, AI_PIECE)


def test_winning_move_vertical():
    board = create_board()
    # Place 4 in a column for PLAYER_PIECE at column 2
    col = 2
    for _ in range(4):
        row = get_next_open_row(board, col)
        board = drop_piece(board, row, col, PLAYER_PIECE)
    assert winning_move(board, PLAYER_PIECE)


def test_winning_move_positive_diagonal():
    board = create_board()
    # Place 4 in a positive-slope diagonal for AI_PIECE
    # Coordinates: (row,col): (0,0),(1,1),(2,2),(3,3)
    for i in range(4):
        # drop pieces below until reaching correct row
        for _ in range(i):
            board = drop_piece(board, get_next_open_row(board, i), i, PLAYER_PIECE)
        board = drop_piece(board, get_next_open_row(board, i), i, AI_PIECE)
    assert winning_move(board, AI_PIECE)


def test_winning_move_negative_diagonal():
    board = create_board()
    # Place 4 in a negative-slope diagonal for PLAYER_PIECE
    # Coordinates: (row,col): (3,0),(2,1),(1,2),(0,3)
    positions = [(3,0),(2,1),(1,2),(0,3)]
    for row, col in positions:
        # drop until row reached
        while get_next_open_row(board, col) < row:
            board = drop_piece(board, get_next_open_row(board, col), col, AI_PIECE)
        board = drop_piece(board, get_next_open_row(board, col), col, PLAYER_PIECE)
    assert winning_move(board, PLAYER_PIECE)


def test_generate_windows_count():
    windows = generate_windows()
    horiz = ROW_COUNT * (COLUMN_COUNT - WINDOW_LENGTH + 1)
    vert = COLUMN_COUNT * (ROW_COUNT - WINDOW_LENGTH + 1)
    diag = 2 * (ROW_COUNT - WINDOW_LENGTH + 1) * (COLUMN_COUNT - WINDOW_LENGTH + 1)
    assert len(windows) == horiz + vert + diag
