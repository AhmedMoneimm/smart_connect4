# views/game_view.py

import pygame
from models.constants import ROW_COUNT, COLUMN_COUNT, SQUARESIZE, RADIUS, BLUE, RED, YELLOW, BLACK, PLAYER_PIECE, AI_PIECE

def draw_board(screen, board):
    # Draw the board background and empty circles.
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE/2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), RADIUS)
    # Draw the pieces
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            piece = board[(ROW_COUNT - 1 - r) * COLUMN_COUNT + c]
            if piece == PLAYER_PIECE or piece == '1':
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE/2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), RADIUS)
            elif piece == AI_PIECE or piece == '2':
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE/2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def print_board(board):
    # Print board as a 2D grid to the console.
    cols = COLUMN_COUNT
    rows = ROW_COUNT
    board_array = []
    for r in range(rows):
        board_array.append([board[r * cols + c] for c in range(cols)])
    print("\nBoard State:")
    for row in range(rows-1, -1, -1):
        print(" ".join(board_array[row]))
