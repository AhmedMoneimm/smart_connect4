# File: tests/test_heuristics.py
import pytest
from models.constants import ROW_COUNT, COLUMN_COUNT, PLAYER_PIECE, AI_PIECE, EMPTY
from models.heuristics import combined_heuristic, evaluate_board
from models.board import generate_windows


def make_empty_board():
    return [EMPTY] * (ROW_COUNT * COLUMN_COUNT)


def test_reward_and_block_weights():
    board = make_empty_board()
    # Opponent has three in a row at row 0 cols 0,1,2
    for c in [0,1,2]:
        idx = c
        board[idx] = PLAYER_PIECE

    # AI should see a block threat
    score_ai = combined_heuristic(board, AI_PIECE)
    score_player = combined_heuristic(board, PLAYER_PIECE)

    assert score_player > 0
    assert score_ai < score_player
    # Ensure block_3 penalty was applied heavily
    assert score_ai < -5000


def test_trap_and_isolation_terms():
    board = make_empty_board()
    # Place AI piece isolated in center
    center_col = COLUMN_COUNT // 2
    r = 0
    board[r * COLUMN_COUNT + center_col] = AI_PIECE
    # No neighbors -> isolation penalty
    base_score = combined_heuristic(board, AI_PIECE)
    assert base_score < 0

    # Add neighbors to form a trap scenario
    board[r * COLUMN_COUNT + (center_col-1)] = AI_PIECE
    board[r * COLUMN_COUNT + (center_col+1)] = AI_PIECE
    trap_score = combined_heuristic(board, AI_PIECE)
    assert trap_score > base_score
