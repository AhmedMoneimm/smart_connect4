import math
import random
import networkx as nx
import heapq
import hashlib

# Global transposition table for caching expectiminimax results
_trans_table_em = {}

def zobrist_hash(board_str):
    return hashlib.md5(board_str.encode('utf-8')).hexdigest()

from models.board import get_valid_locations, get_next_open_row, drop_piece
from models.constants import PLAYER_PIECE, AI_PIECE
from models.heuristics import evaluate_board

def expectiminimax(board, depth, alpha, beta, maximizing,
                   piece=AI_PIECE, visualize=False,
                   graph=None, id_counter=None, node_id=None,
                   strategy="combined", prune_threshold=0):
    """
    Optimized ExpectiMinimax with alpha-beta pruning, transposition caching,
    optional visualization, and heuristic pruning.
    """
    # ----- Visualization setup -----
    if visualize:
        if graph is None:
            graph = nx.DiGraph()
        if id_counter is None:
            id_counter = {"next": 0}
        if node_id is None:
            node_id = id_counter["next"]
            id_counter["next"] += 1

    # ----- Transposition table lookup -----
    board_str = "".join(board)  # Convert the board state to a string representation
    key = (zobrist_hash(board_str), depth, maximizing, piece, strategy)
    if not visualize and key in _trans_table_em:
        return (*_trans_table_em[key], graph)

    # ----- Check terminal state -----
    valid_cols = get_valid_locations(board)
    if depth == 0 or not valid_cols:
        score = evaluate_board(board, piece, strategy)
        if visualize:
            graph.add_node(node_id, label=str(score))
        return None, score, graph

    # Opponent's piece and move piece determination
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    move_piece = piece if maximizing else opp_piece

    # ----- Generate children nodes -----
    children = []
    for col in valid_cols:
        row = get_next_open_row(board, col)
        new_board = drop_piece(board, row, col, move_piece)
        h = evaluate_board(new_board, piece, strategy)
        children.append((col, new_board, h))

    # Use heapq.nlargest to get the top children based on the heuristic value
    children = heapq.nlargest(5, children, key=lambda x: x[2] if maximizing else -x[2])

    # ----- Alpha-beta pruning -----
    best_val = -math.inf if maximizing else math.inf
    best_col = random.choice(valid_cols)

    # Branching weights (main, left, right)
    weights = [(0, 0.6), (-1, 0.2), (1, 0.2)]

    # ----- Explore each child -----
    for col, main_board, _ in children:
        total = 0.0
        for offset, weight in weights:
            sub_col = col + offset
            if sub_col not in valid_cols:
                continue
            row = get_next_open_row(main_board, sub_col)
            if row is None:
                continue
            sub_board = drop_piece(main_board, row, sub_col, move_piece)

            # Heuristic pruning: evaluate before recursing deeper.
            if prune_threshold > 0:
                approx_score = evaluate_board(sub_board, piece, strategy)
                if maximizing and approx_score < alpha - prune_threshold:
                    continue
                if not maximizing and approx_score > beta + prune_threshold:
                    continue

            # Recursively call expectiminimax for the next move
            child_id = None
            if visualize:
                child_id = id_counter["next"]
                id_counter["next"] += 1

            _, score, graph = expectiminimax(
                sub_board, depth - 1,
                alpha, beta, not maximizing,
                piece, visualize, graph, id_counter, child_id,
                strategy, prune_threshold
            )
            total += weight * score

            # Visualization updates
            if visualize:
                graph.add_node(node_id, label=f"{total:.1f}")
                graph.add_edge(node_id, child_id)

        # Update best value and column
        if maximizing:
            if total > best_val:
                best_val, best_col = total, col
            alpha = max(alpha, best_val)
        else:
            if total < best_val:
                best_val, best_col = total, col
            beta = min(beta, best_val)

        # Alpha-beta cutoff
        if alpha >= beta:
            break

    # Cache result in transposition table (without graph)
    if not visualize:
        _trans_table_em[key] = (best_col, best_val)

    return best_col, best_val, graph
