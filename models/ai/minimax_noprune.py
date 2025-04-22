import math
import random
import networkx as nx

from models.board import get_valid_locations, get_next_open_row, drop_piece
from models.constants import PLAYER_PIECE, AI_PIECE, EMPTY, ROW_COUNT, COLUMN_COUNT
from models.heuristics import evaluate_board  # relative path: models/heuristics.py

# Transposition table to cache evaluations: {(board_key, depth, maximizing, strategy): (col, score)}
_transposition_table = {}

def minimax_noprune(board, depth, maximizingPlayer,
                    piece=AI_PIECE,
                    visualize=False,
                    strategy="combined",
                    graph=None,
                    id_counter=None,
                    node_id=None):
    """
    Depth-limited Minimax without alpha-beta pruning,
    but with heuristic move-ordering and caching.
    Signature matches: minimax_noprune(board, depth, True, AI_PIECE, visualize)
    """
    # Visualization setup
    if visualize and graph is None:
        graph = nx.DiGraph()
    if visualize and id_counter is None:
        id_counter = {"next": 0}
    if visualize and node_id is None:
        node_id = id_counter["next"]
        id_counter["next"] += 1

    # Transposition key includes heuristic strategy
    key = (tuple(board), depth, maximizingPlayer, strategy)
    if not visualize and key in _transposition_table:
        col, score = _transposition_table[key]
        return col, score, graph

    valid_cols = get_valid_locations(board)
    terminal = (depth == 0) or (not valid_cols)

    # Terminal evaluation
    if terminal:
        score = evaluate_board(board, piece, strategy=strategy)
        if visualize:
            graph.add_node(node_id, label=str(score))
        result = (None, score, graph)
    else:
        # Prepare children with heuristic values for ordering
        opponent = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
        children = []
        for col in valid_cols:
            row = get_next_open_row(board, col)
            new_board = drop_piece(
                board, row, col,
                piece if maximizingPlayer else opponent
            )
            # Heuristic evaluation at 1-ply for ordering
            h_val = evaluate_board(new_board, piece, strategy=strategy)
            children.append((col, new_board, h_val))

        # Sort by heuristic: high->low for maximize, low->high for minimize
        children.sort(key=lambda x: x[2], reverse=maximizingPlayer)

        best_col = random.choice([c for c, _, _ in children])
        best_val = -math.inf if maximizingPlayer else math.inf

        # Recurse through all ordered children (no pruning)
        for col, child_board, _ in children:
            # Visualization nodes
            child_id = None
            if visualize:
                child_id = id_counter["next"]
                id_counter["next"] += 1

            _, child_score, graph = minimax_noprune(
                child_board,
                depth - 1,
                not maximizingPlayer,
                piece,
                visualize,
                strategy,
                graph,
                id_counter,
                child_id
            )

            if visualize:
                graph.add_node(node_id, label=f"{best_val:.1f}")
                graph.add_edge(node_id, child_id)

            if maximizingPlayer:
                if child_score > best_val:
                    best_val = child_score
                    best_col = col
            else:
                if child_score < best_val:
                    best_val = child_score
                    best_col = col

        result = (best_col, best_val, graph)

    # Cache result when not visualizing
    if not visualize:
        _transposition_table[key] = result[:2]

    return result


# ----------------------------------------------------------------------------
# Example usage of heuristics & minimax_noprune:
#
# from models.heuristics import evaluate_board
# from models.minimax_noprune import minimax_noprune
#
# board = [EMPTY] * (ROW_COUNT * COLUMN_COUNT)
# piece = AI_PIECE
# depth = 4
# visualize = False
#
# # Basic heuristic ordering
# col, score, graph = minimax_noprune(
#     board, depth, True,
#     piece,
#     visualize,
#     strategy="basic"
# )
# print(f"Chosen move: {col}, Score: {score}")
#
# # Aware heuristic ordering
# col, score, graph = minimax_noprune(
#     board, depth, True,
#     piece,
#     visualize,
#     strategy="combined"
# )
# print(f"Chosen move: {col}, Score: {score}")
# ----------------------------------------------------------------------------
