from models.constants import ROW_COUNT, COLUMN_COUNT, EMPTY, PLAYER_PIECE, AI_PIECE, WINDOW_LENGTH

# Precompute index ranges for windows only once
WINDOWS = []
for r in range(ROW_COUNT):
    for c in range(COLUMN_COUNT - 3):
        WINDOWS.append([r * COLUMN_COUNT + c + i for i in range(4)])
for c in range(COLUMN_COUNT):
    for r in range(ROW_COUNT - 3):
        WINDOWS.append([(r + i) * COLUMN_COUNT + c for i in range(4)])
for r in range(ROW_COUNT - 3):
    for c in range(COLUMN_COUNT - 3):
        WINDOWS.append([(r + i) * COLUMN_COUNT + (c + i) for i in range(4)])
for r in range(3, ROW_COUNT):
    for c in range(COLUMN_COUNT - 3):
        WINDOWS.append([(r - i) * COLUMN_COUNT + (c + i) for i in range(4)])

def create_board():
    return EMPTY * (ROW_COUNT * COLUMN_COUNT)

def drop_piece(board, row, col, piece):
    """Drop a piece at (row, col) by string replacement (no list conversion)."""
    idx = row * COLUMN_COUNT + col
    return f"{board[:idx]}{piece}{board[idx+1:]}"  # Faster than full string slicing

def is_valid_location(board, col):
    return board[(ROW_COUNT - 1) * COLUMN_COUNT + col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r * COLUMN_COUNT + col] == EMPTY:
            return r
    return None

def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

def is_board_full(board):
    return EMPTY not in board

def is_terminal_node(board):
    return is_board_full(board)

def winning_move(board, piece):
    for window in WINDOWS:
        if all(board[i] == piece for i in window):
            return True
    return False

def evaluate_window(window_str, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    count_piece = window_str.count(piece)
    count_empty = window_str.count(EMPTY)
    count_opp = window_str.count(opp_piece)

    if count_piece == 4:
        score += 50
    elif count_piece == 3 and count_empty == 1:
        score += 8
    elif count_piece == 2 and count_empty == 2:
        score += 4

    if count_opp == 3 and count_empty == 1:
        score -= 20
    elif count_opp == 2 and count_empty == 2:
        score -= 3

    return score

def score_position(board, piece):
    score = 0
    center_col = COLUMN_COUNT // 2
    center_count = sum(board[r * COLUMN_COUNT + center_col] == piece for r in range(ROW_COUNT))
    score += center_count * 3

    for window in WINDOWS:
        window_str = ''.join(board[i] for i in window)
        score += evaluate_window(window_str, piece)

    return score

def check_winner(board):
    score = {PLAYER_PIECE: 0, AI_PIECE: 0}

    def count_in_direction(row, col, d_row, d_col, player):
        count = 0
        while 0 <= row < ROW_COUNT and 0 <= col < COLUMN_COUNT and board[row * COLUMN_COUNT + col] == player:
            count += 1
            row += d_row
            col += d_col
        return count

    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT):
            piece = board[row * COLUMN_COUNT + col]
            if piece != EMPTY:
                for d_row, d_col in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    if count_in_direction(row, col, d_row, d_col, piece) >= 4:
                        score[piece] += 1
    return score

def string_to_board(board_str, cols=COLUMN_COUNT, rows=ROW_COUNT):
    return [[board_str[row * cols + col] for col in range(cols)] for row in range(rows)]

def board_to_string(board_array):
    return ''.join(cell for row in board_array for cell in row)

def generate_windows():
    return WINDOWS  # Already precomputed at the top

def is_playable(board, idx):
    col = idx % COLUMN_COUNT
    next_row = get_next_open_row(board, col)
    return next_row is not None and next_row * COLUMN_COUNT + col == idx
