import math  # Import math module for mathematical functions
import random  # Import random module for random choices
import networkx as nx  # Import networkx for graph visualization support
import hashlib  # Import hashlib for hashing functions (currently not used)

# Cache for expectiminimax
_trans_table_em = {}  # Initialize transposition table to cache computed results

from models.board import get_valid_locations, get_next_open_row, drop_piece  # Import board helper functions
from models.constants import PLAYER_PIECE, AI_PIECE  # Import constants representing player and AI pieces
from models.heuristics import evaluate_board  # Import board evaluation heuristic

def expectiminimax(board, depth, alpha, beta, maximizing,
                   piece=AI_PIECE, visualize=False,
                   graph=None, id_counter=None, node_id=None,
                   strategy="combined", prune_threshold=0):  # Define expectiminimax function with parameters
    # --- Visualization setup ---
    if visualize:  # Check if visualizing the decision process
        if graph is None:  # If no graph is provided, create a new directed graph
            graph = nx.DiGraph()  # Initialize a new directed graph
        if id_counter is None:  # If no ID counter is provided, initialize one
            id_counter = {"next": 0}  # Set starting node ID to 0
        if node_id is None:  # If no node ID is provided, use the first available ID from the counter
            node_id = id_counter["next"]  # Assign current counter value to node_id
            id_counter["next"] += 1  # Increment the counter for the next node
        graph.add_node(node_id,
                       label='MAX' if maximizing else 'MIN',
                       node_type='decision')  # Add a node to the graph indicating a decision point (MAX or MIN)

    # --- Transposition lookup ---
    key = (hash("".join(board)), depth, maximizing, piece, strategy)  # Generate a unique key for the current state
    if not visualize and key in _trans_table_em:  # If not visualizing and state already computed
        return (*_trans_table_em[key], graph)  # Return cached best move and value along with the graph

    valid_cols = get_valid_locations(board)  # Get all valid columns where a move is possible
    # Terminal node?
    if depth == 0 or not valid_cols:  # If maximum depth reached or no valid moves left
        score = evaluate_board(board, piece, strategy)  # Evaluate the board state with a heuristic
        if visualize:  # If visualizing, update the node's label with the score
            graph.nodes[node_id]['label'] = str(score)  # Set node label to the evaluated score
        return None, score, graph  # Return terminal score with no move (None)

    # Determine who plays
    opp = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE  # Determine opponent's piece based on current piece
    move_piece = piece if maximizing else opp  # Select which piece to move depending on maximizing status

    best_val = -math.inf if maximizing else math.inf  # Initialize best value (worst for max, best for min)
    best_col = random.choice(valid_cols)  # Initialize best column with a random valid move

    # For each possible move
    for col in valid_cols:  # Loop through each valid column
        row = get_next_open_row(board, col)  # Find the next available row for the column
        main_b = drop_piece(board, row, col, move_piece)  # Simulate dropping the piece into the board

        # -- decision‐node child for playing in 'col' --
        if visualize:  # Check if visualizing the decision nodes
            dec = id_counter['next']  # Generate a new node ID for the decision node
            id_counter['next'] += 1  # Increment the node ID counter
            graph.add_node(dec, label=f"col={col}", node_type='decision')  # Add decision node representing move at col
            graph.add_edge(node_id, dec)  # Create an edge from parent node to decision node
        else:
            dec = None  # If not visualizing, set decision node identifier to None

        # Build chance‐node offsets (col, col-1, col+1)
        offsets = [0]  # Start with no offset (direct drop)
        if col - 1 in valid_cols: offsets.append(-1)  # Append left offset if valid
        if col + 1 in valid_cols: offsets.append(1)  # Append right offset if valid
        neighbors = len(offsets) - 1  # Determine the number of neighboring moves (excluding the direct one)
        neigh_w = 0.2 if neighbors == 2 else 0.4 if neighbors == 1 else 0.0  # Assign weight for neighbor moves
        weights = [(off, 0.6 if off == 0 else neigh_w) for off in offsets]  # Create a list of offsets with corresponding weights

        total = 0.0  # Initialize total score for the current column move
        for off, w in weights:  # Loop over each offset and its weight
            sub_col = col + off  # Calculate the actual sub-column by adding the offset
            if sub_col not in valid_cols:  # If the computed sub-column is invalid, skip this variation
                continue  # Continue to next offset
            r = get_next_open_row(main_b, sub_col)  # Determine the next open row for the sub-column
            if r is None:  # If no open row exists, skip this branch
                continue  # Continue to next offset
            sb = drop_piece(main_b, r, sub_col, move_piece)  # Drop the piece in the sub-column to get a new board

            # Heuristic‐based pruning
            if prune_threshold > 0:  # If a prune threshold is specified
                approx = evaluate_board(sb, piece, strategy)  # Approximate board score using heuristic
                if maximizing and approx < alpha - prune_threshold:  # For maximizing, prune if score is too low
                    continue  # Skip further evaluation in this branch
                if not maximizing and approx > beta + prune_threshold:  # For minimizing, prune if score is too high
                    continue  # Skip further evaluation in this branch

            if visualize:  # If visualization is on, create a chance node
                # -- chance‐node --
                ch = id_counter['next']  # Generate new node ID for the chance node
                id_counter['next'] += 1  # Increment node ID counter
                graph.add_node(ch, label=f"P={w:.2f}", node_type='chance')  # Add chance node with probability label
                graph.add_edge(dec, ch)  # Connect decision node to chance node

                # Reserve an ID for the child of this chance node
                nxt = id_counter['next']  # Generate a new ID for the recursive child
                id_counter['next'] += 1  # Increment node ID counter

                # **Add the missing edge** from chance to its recursive child
                graph.add_edge(ch, nxt)  # Link chance node to its recursive child node
            else:
                ch = None  # If not visualizing, set chance node to None
                nxt = None  # Set recursive child node to None

            # Recurse under the chance node
            _, score, graph = expectiminimax(
                sb, depth - 1, alpha, beta, not maximizing,
                piece, visualize, graph, id_counter, nxt,
                strategy, prune_threshold
            )  # Recursively evaluate the new board state with decreased depth and alternate perspective
            total += w * score  # Accumulate the weighted score from this branch

            if visualize:  # If visualization is active
                # Update chance‐node label to show weight & resulting score
                graph.nodes[ch]['label'] = f"{w:.2f}\n{score:.2f}"  # Modify chance node label with weight and evaluated score

        # Alpha‐beta updates
        if maximizing:  # If evaluating a maximizing node
            if total > best_val:  # If the accumulated score is better than current best
                best_val, best_col = total, col  # Update best value and best column for maximizing player
            alpha = max(alpha, best_val)  # Refresh alpha with the maximum of its current value and best value found
        else:  # For a minimizing node
            if total < best_val:  # If the accumulated score is lower than current best
                best_val, best_col = total, col  # Update best value and best column for minimizing player
            beta = min(beta, best_val)  # Refresh beta with the minimum of its current value and best value found
        if alpha >= beta:  # Check if pruning condition is met
            break  # Terminate further exploration if alpha-beta condition holds

    if not visualize:  # If not in visualization mode
        _trans_table_em[key] = (best_col, best_val)  # Cache the computed result in the transposition table

    return best_col, best_val, graph  # Return the best move column, its evaluated value, and the graph structure
