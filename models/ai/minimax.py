import math
import random
import networkx as nx

from models.board import get_valid_locations, get_next_open_row, drop_piece
from models.constants import PLAYER_PIECE, AI_PIECE, EMPTY, ROW_COUNT, COLUMN_COUNT
from models.heuristics import evaluate_board  # relative path: models/heuristics.py

# Transposition table to cache evaluations for alpha-beta: {(board_key, depth, maximizing, strategy): (col, score)}
_transposition_table_ab = {}

def minimax(board, depth, alpha, beta, maximizingPlayer,
            piece=AI_PIECE,
            visualize=False,
            strategy="combined",
            graph=None,
            id_counter=None,
            node_id=None):
    """
    Depth-limited Minimax with alpha-beta pruning,
    heuristic move-ordering and caching.
    Signature: minimax(board, depth, -inf, inf, True, AI_PIECE, visualize)
    Returns (col, score, graph).
    """
    # Visualization setup
    if visualize and graph is None:
        graph = nx.DiGraph()
    if visualize and id_counter is None:
        id_counter = {"next": 0}
    if visualize and node_id is None:
        node_id = id_counter["next"]
        id_counter["next"] += 1
        graph.add_node(node_id, label="")  # initialize placeholder label

    # Transposition key excludes alpha/beta bounds
    key = (tuple(board), depth, maximizingPlayer, strategy)
    if not visualize and key in _transposition_table_ab:
        col, score = _transposition_table_ab[key]
        return col, score, graph

    valid_cols = get_valid_locations(board)
    terminal = (depth == 0) or (not valid_cols)

    # Terminal evaluation
    if terminal:
        score = evaluate_board(board, piece, strategy=strategy)
        if visualize:
            graph.nodes[node_id]['label'] = str(score)
        result_col, result_score = None, score
    else:
        opponent = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
        # Prepare children with heuristic values
        children = []
        for col in valid_cols:
            row = get_next_open_row(board, col)
            new_board = drop_piece(
                board, row, col,
                piece if maximizingPlayer else opponent
            )
            h_val = evaluate_board(new_board, piece, strategy=strategy)
            children.append((col, new_board, h_val))

        # Sort by heuristic
        children.sort(key=lambda x: x[2], reverse=maximizingPlayer)

        # Initialize bests and bounds
        best_val = -math.inf if maximizingPlayer else math.inf
        result_col = random.choice([c for c, _, _ in children])

        # Recurse with pruning
        for col, child_board, _ in children:
            child_id = None
            if visualize:
                child_id = id_counter['next']
                id_counter['next'] += 1
                graph.add_node(child_id, label="")  # placeholder

            _, child_score, graph = minimax(
                child_board,
                depth - 1,
                alpha,
                beta,
                not maximizingPlayer,
                piece,
                visualize,
                strategy,
                graph,
                id_counter,
                child_id
            )

            # Update best_val and bounds
            if maximizingPlayer:
                if child_score > best_val:
                    best_val = child_score
                    result_col = col
                alpha = max(alpha, best_val)
            else:
                if child_score < best_val:
                    best_val = child_score
                    result_col = col
                beta = min(beta, best_val)

            # Draw after updating real value
            if visualize:
                graph.nodes[node_id]['label'] = f"{best_val:.1f}"
                graph.add_edge(node_id, child_id)

            # Alpha-beta cutoff
            if beta <= alpha:
                break

        result_score = best_val

    # Cache result
    if not visualize:
        _transposition_table_ab[key] = (result_col, result_score)

    return result_col, result_score, graph

# Example usage:
# col, score, graph = minimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize=True)
# draw_graph_process(graph, col)