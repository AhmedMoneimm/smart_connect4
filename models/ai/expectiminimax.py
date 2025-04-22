import math
import random
import networkx as nx
import hashlib

# Cache for expectiminimax
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
    # --- Visualization setup ---
    if visualize:
        if graph is None:
            graph = nx.DiGraph()
        if id_counter is None:
            id_counter = {"next": 0}
        if node_id is None:
            node_id = id_counter["next"]
            id_counter["next"] += 1
        graph.add_node(node_id,
                       label='MAX' if maximizing else 'MIN',
                       node_type='decision')

    # --- Transposition lookup ---
    key = (zobrist_hash("".join(board)), depth, maximizing, piece, strategy)
    if not visualize and key in _trans_table_em:
        return (*_trans_table_em[key], graph)

    valid_cols = get_valid_locations(board)
    # Terminal node?
    if depth == 0 or not valid_cols:
        score = evaluate_board(board, piece, strategy)
        if visualize:
            graph.nodes[node_id]['label'] = str(score)
        return None, score, graph

    # Determine who plays
    opp = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    move_piece = piece if maximizing else opp

    best_val = -math.inf if maximizing else math.inf
    best_col = random.choice(valid_cols)

    # For each possible move
    for col in valid_cols:
        row = get_next_open_row(board, col)
        main_b = drop_piece(board, row, col, move_piece)

        # -- decision‐node child for playing in 'col' --
        if visualize:
            dec = id_counter['next']
            id_counter['next'] += 1
            graph.add_node(dec, label=f"col={col}", node_type='decision')
            graph.add_edge(node_id, dec)
        else:
            dec = None

        # Build chance‐node offsets (col, col-1, col+1)
        offsets = [0]
        if col - 1 in valid_cols: offsets.append(-1)
        if col + 1 in valid_cols: offsets.append(1)
        neighbors = len(offsets) - 1
        neigh_w = 0.2 if neighbors == 2 else 0.4 if neighbors == 1 else 0.0
        weights = [(off, 0.6 if off == 0 else neigh_w) for off in offsets]

        total = 0.0
        for off, w in weights:
            sub_col = col + off
            if sub_col not in valid_cols:
                continue
            r = get_next_open_row(main_b, sub_col)
            if r is None:
                continue
            sb = drop_piece(main_b, r, sub_col, move_piece)

            # Heuristic‐based pruning
            if prune_threshold > 0:
                approx = evaluate_board(sb, piece, strategy)
                if maximizing and approx < alpha - prune_threshold:
                    continue
                if not maximizing and approx > beta + prune_threshold:
                    continue

            if visualize:
                # -- chance‐node --
                ch = id_counter['next']
                id_counter['next'] += 1
                graph.add_node(ch, label=f"P={w:.2f}", node_type='chance')
                graph.add_edge(dec, ch)

                # Reserve an ID for the child of this chance node
                nxt = id_counter['next']
                id_counter['next'] += 1

                # **Add the missing edge** from chance to its recursive child
                graph.add_edge(ch, nxt)
            else:
                ch = None
                nxt = None

            # Recurse under the chance node
            _, score, graph = expectiminimax(
                sb, depth - 1, alpha, beta, not maximizing,
                piece, visualize, graph, id_counter, nxt,
                strategy, prune_threshold
            )
            total += w * score

            if visualize:
                # Update chance‐node label to show weight & resulting score
                graph.nodes[ch]['label'] = f"{w:.2f}\n{score:.2f}"

        # Alpha‐beta updates
        if maximizing:
            if total > best_val:
                best_val, best_col = total, col
            alpha = max(alpha, best_val)
        else:
            if total < best_val:
                best_val, best_col = total, col
            beta = min(beta, best_val)
        if alpha >= beta:
            break

    if not visualize:
        _trans_table_em[key] = (best_col, best_val)

    return best_col, best_val, graph
