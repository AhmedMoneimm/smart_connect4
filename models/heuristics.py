# Import necessary functions and constants from related modules
from models.board import score_position, generate_windows, is_playable  # Functions for board analysis and move legality
from models.constants import ROW_COUNT, COLUMN_COUNT, PLAYER_PIECE, AI_PIECE, EMPTY  # Game constants

# Precompute all 4-cell windows (possible winning alignments on the board)
WINDOWS = generate_windows()  # List of index groups that form 4-cell sequences on the board

# Define heuristic weights for different board situations
WEIGHTS = {
    "center_control": 6,        # Weight for controlling the center column
    "reward_4": 10000,          # Reward for forming a 4-piece connection
    "reward_3": 100,            # Reward for forming a 3-piece connection with a blocking empty cell
    "reward_2": 10,             # Reward for forming a 2-piece connection
    "reward_1": 1,              # Reward for forming a single piece pattern
    "block_3": 10000000,        # Penalty for opponent's 3-piece threat with an empty cell
    "block_2": 100,             # Penalty for opponent's 2-piece threat, even if not immediate
    "trap_bonus": 1500,         # Additional bonus for setting up a trap move
    "isolation_penalty": 50,    # Penalty for pieces that have no friendly neighbors
}

# Define neighbor index deltas to check for isolation (adjacent indices horizontally and vertically)
NEIGHBOR_DELTAS = [-1, 1, -COLUMN_COUNT, COLUMN_COUNT]  # Left, Right, Above, Below

def combined_heuristic(board, piece):
    # Determine the opponent's piece based on the current player's piece
    opponent = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE  # Choose opponent's piece
    score = score_position(board, piece)  # Initialize score with base position evaluation

    # Add bonus for controlling the center column
    center_idx = COLUMN_COUNT // 2  # Compute index of the center column
    score += sum(
        1 for r in range(ROW_COUNT) if board[r * COLUMN_COUNT + center_idx] == piece  # Count how many pieces are in the center column
    ) * WEIGHTS["center_control"]  # Multiply count by the center control weight

    # Loop through each precomputed 4-cell window (potential winning sequences)
    for window in WINDOWS:  
        # Retrieve the board cells corresponding to the indices in the current window
        cells = [board[i] for i in window]  
        yours = theirs = empties = 0  # Initialize counts for player's pieces, opponent's pieces, and empty cells

        # Count the occurrences of the player's piece, opponent's piece, and empties in the current window
        for c in cells:
            if c == piece:
                yours += 1  # Increment player's piece count
            elif c == opponent:
                theirs += 1  # Increment opponent's piece count
            elif c == EMPTY:
                empties += 1  # Increment empty cell count

        # --- Offensive Rewards ---
        if yours == 4:
            score += WEIGHTS["reward_4"]  # Add large reward if the player has a winning move
        elif yours == 3 and empties == 1:
            empty_idx = window[cells.index(EMPTY)]  # Identify the index of the empty cell in a potential win
            if is_playable(board, empty_idx):
                score += WEIGHTS["reward_3"] + WEIGHTS["trap_bonus"]  # Reward if the move is playable and creates a trap
        elif yours == 2 and empties == 2:
            score += WEIGHTS["reward_2"]  # Reward for a 2-piece alignment with potential to expand
        elif yours == 1 and empties == 3:
            score += WEIGHTS["reward_1"]  # Minimal reward for a single piece in a window

        # --- Defensive Penalties ---
        if theirs == 3 and empties == 1:
            empty_idx = window[cells.index(EMPTY)]  # Identify the critical empty cell for opponent's potential win
            if is_playable(board, empty_idx):
                score -= WEIGHTS["block_3"]  # Deduct heavy penalty if opponent is close to winning
        elif theirs == 2 and empties == 2:
            score -= WEIGHTS["block_2"]  # Deduct penalty for opponent's potential threat

    # --- Isolation penalty ---
    # Loop over each cell in the board to check for isolated pieces
    for idx, cell in enumerate(board):
        if cell == piece:  # Only consider cells occupied by the player's piece
            if all(
                0 <= idx + delta < ROW_COUNT * COLUMN_COUNT and board[idx + delta] != piece  # Check neighbors are within bounds and not the player's piece
                for delta in NEIGHBOR_DELTAS
            ):
                score -= WEIGHTS["isolation_penalty"]  # Deduct penalty if piece is isolated (no friendly neighbors)

    return score  # Return the final heuristic score for the board

# Map heuristic strategies to their functions (currently only "combined" strategy is implemented)
HEURISTICS = {
    "combined": combined_heuristic,  # Associate the combined heuristic function with the key "combined"
}

def evaluate_board(board, piece, strategy="combined"):
    try:
        return HEURISTICS[strategy](board, piece)  # Evaluate board using the selected heuristic strategy
    except KeyError:
        raise ValueError(f"Unknown strategy: {strategy}")  # Raise error if an unknown strategy is specified
