from models.board import score_position, generate_windows, is_playable
from models.constants import ROW_COUNT, COLUMN_COUNT, PLAYER_PIECE, AI_PIECE, EMPTY

# --- Precompute all 4-cell windows ---
WINDOWS = generate_windows()

# --- Heuristic Weights ---
WEIGHTS = {
    "center_control": 6,
    "reward_4": 10000,
    "reward_3": 100,
    "reward_2": 10,
    "reward_1": 1,
    "block_3": 10000000,
    "block_2": 100,
    "trap_bonus": 1500,
    "isolation_penalty": 50,
}

# --- Precompute neighbor deltas for isolation ---
NEIGHBOR_DELTAS = [-1, 1, -COLUMN_COUNT, COLUMN_COUNT]

def combined_heuristic(board, piece):
    opponent = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    score = score_position(board, piece)

    # Center control bonus (precomputed center column)
    center_idx = COLUMN_COUNT // 2
    score += sum(
        1 for r in range(ROW_COUNT) if board[r * COLUMN_COUNT + center_idx] == piece
    ) * WEIGHTS["center_control"]

    for window in WINDOWS:
        cells = [board[i] for i in window]
        yours = theirs = empties = 0

        for c in cells:
            if c == piece:
                yours += 1
            elif c == opponent:
                theirs += 1
            elif c == EMPTY:
                empties += 1

        # --- Offensive Rewards ---
        if yours == 4:
            score += WEIGHTS["reward_4"]
        elif yours == 3 and empties == 1:
            empty_idx = window[cells.index(EMPTY)]
            if is_playable(board, empty_idx):
                score += WEIGHTS["reward_3"] + WEIGHTS["trap_bonus"]
        elif yours == 2 and empties == 2:
            score += WEIGHTS["reward_2"]
        elif yours == 1 and empties == 3:
            score += WEIGHTS["reward_1"]

        # --- Defensive Penalties ---
        if theirs == 3 and empties == 1:
            empty_idx = window[cells.index(EMPTY)]
            if is_playable(board, empty_idx):
                score -= WEIGHTS["block_3"]
        elif theirs == 2 and empties == 2:
            score -= WEIGHTS["block_2"]

    # --- Isolation penalty ---
    for idx, cell in enumerate(board):
        if cell == piece:
            if all(
                0 <= idx + delta < ROW_COUNT * COLUMN_COUNT and board[idx + delta] != piece
                for delta in NEIGHBOR_DELTAS
            ):
                score -= WEIGHTS["isolation_penalty"]

    return score

# Strategy map
HEURISTICS = {
    "combined": combined_heuristic,
}

def evaluate_board(board, piece, strategy="combined"):
    try:
        return HEURISTICS[strategy](board, piece)
    except KeyError:
        raise ValueError(f"Unknown strategy: {strategy}")
