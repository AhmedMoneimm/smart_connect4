# game_controller.py

import math
import random
import sys
import time
import multiprocessing
import pygame

from models.board import (
    create_board,
    is_valid_location,
    get_next_open_row,
    drop_piece,
    is_board_full,
    check_winner,
)
from models.constants import (
    ROW_COUNT,
    COLUMN_COUNT,
    SQUARESIZE,
    PLAYER,      # PLAYER constant (typically 0)
    AI,          # AI constant (typically 1)
    PLAYER_PIECE,
    AI_PIECE,
    BLACK,
    RED,
)
from views.game_view import draw_board, print_board
from models.ai.minimax import minimax
from models.ai.minimax_noprune import minimax_noprune
from models.ai.expectiminimax import expectiminimax

from utils.tree_visualizer import draw_graph_process

def main():
    # Initialize Pygame and the main window
    pygame.init()
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Connect 4")

    # Parse command-line args
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    visualize = bool(int(sys.argv[3])) if len(sys.argv) > 3 else False
    selected_ai = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    board = create_board()
    game_over = False

    # Set turn so that Player 1 always starts
    turn = PLAYER

    draw_board(screen, board)
    clock = pygame.time.Clock()

    while not game_over:
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                # Draw the hovering piece
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(
                        screen, RED, (posx, int(SQUARESIZE / 2)), SQUARESIZE // 2 - 5
                    )
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
                # Player click: drop their piece
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = posx // SQUARESIZE
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    board = drop_piece(board, row, col, PLAYER_PIECE)
                    print_board(board)
                    draw_board(screen, board)
                    turn = AI

        # AI's turn
        if turn == AI and not is_board_full(board):
            start = time.time()
            graph = None

            # Run the chosen search algorithm and get the best move, score, and search graph.
            if selected_ai == 1:
                col, score, graph = minimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize)
            elif selected_ai == 2:
                col, score, graph = minimax_noprune(board, depth, True, AI_PIECE, visualize)
            elif selected_ai == 3:
                col, score, graph = expectiminimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize)
            else:
                col, score, graph = minimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize)
            end = time.time()

            # Validate the AI's chosen column
            valid_cols = [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]
            if col not in valid_cols:
                fallback = valid_cols[0] if valid_cols else None
                print(
                    f"Warning: AI wanted column {col}, but it's full. "
                    f"Falling back to {fallback}."
                )
                col = fallback

            # Print the AI's suggested move and its evaluation score
            if not visualize and col is not None:
                print(f"AI suggests column {col + 1} with score {score}")

            # Drop the AI's piece if the move is valid
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                board = drop_piece(board, row, col, AI_PIECE)
                print_board(board)
                draw_board(screen, board)
                print(f"AI move computed in {end - start:.2f} seconds with score: {score}")

                # Launch the tree visualizer if requested
                if visualize and graph is not None:
                    best_move = col
                    p = multiprocessing.Process(
                        target=draw_graph_process, args=(graph, best_move)
                    )
                    p.daemon = True
                    p.start()

                turn = PLAYER

            # Check for end-of-game
            if is_board_full(board):
                winners = check_winner(board)
                if winners[PLAYER_PIECE] > winners[AI_PIECE]:
                    print("Player wins!")
                elif winners[PLAYER_PIECE] < winners[AI_PIECE]:
                    print("AI wins!")
                else:
                    print("It is a draw!")
                pygame.time.wait(3000)
                game_over = True

            clock.tick(30)

if __name__ == "__main__":
    # Ensure clean spawn for new processes
    multiprocessing.set_start_method("spawn", force=True)
    main()
