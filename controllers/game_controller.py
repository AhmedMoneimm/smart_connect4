import math
import random
import sys
import time
import multiprocessing
import pygame

from models.board import (
    create_board, is_valid_location, get_next_open_row,
    drop_piece, is_board_full, check_winner
)
from models.constants import (
    ROW_COUNT, COLUMN_COUNT, SQUARESIZE,
    PLAYER, AI, PLAYER_PIECE, AI_PIECE,
    BLACK, RED
)
from views.game_view import draw_board, print_board
from models.ai.minimax import minimax
from models.ai.minimax_noprune import minimax_noprune
from models.ai.expectiminimax import expectiminimax
from utils.tree_visualizer import draw_graph_process


def main():
    pygame.init()
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Connect 4")

    depth = int(sys.argv[2]) if len(sys.argv)>2 else 3
    visualize = bool(int(sys.argv[3])) if len(sys.argv)>3 else False
    selected_ai = int(sys.argv[1]) if len(sys.argv)>1 else 1

    board = create_board()
    game_over = False
    turn = PLAYER

    draw_board(screen, board)
    clock = pygame.time.Clock()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0,width,SQUARESIZE))
                posx = event.pos[0]
                if turn==PLAYER:
                    pygame.draw.circle(screen, RED, (posx, SQUARESIZE//2), SQUARESIZE//2-5)
                pygame.display.update()

            if event.type==pygame.MOUSEBUTTONDOWN and turn==PLAYER:
                pygame.draw.rect(screen, BLACK, (0,0,width,SQUARESIZE))
                col = event.pos[0]//SQUARESIZE
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    board = drop_piece(board, row, col, PLAYER_PIECE)
                    print_board(board)
                    draw_board(screen, board)
                    turn = AI

        if turn==AI and not is_board_full(board):
            start = time.time()
            graph = None
            # choose AI
            if selected_ai==1:
                col, score, graph = minimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize)
            elif selected_ai==2:
                col, score, graph = minimax_noprune(board, depth, True, AI_PIECE, visualize)
            elif selected_ai==3:
                col, score, graph = expectiminimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize)
            else:
                col, score, graph = minimax(board, depth, -math.inf, math.inf, True, AI_PIECE, visualize)
            end = time.time()

            valid = [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]
            if col not in valid:
                fallback = valid[0] if valid else None
                print(f"Warning: AI wanted column {col}, but it's full. Falling back to {fallback}.")
                col = fallback

            if not visualize and col is not None:
                print(f"AI suggests column {col+1} with score {score}")

            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                board = drop_piece(board, row, col, AI_PIECE)
                print_board(board)
                draw_board(screen, board)
                print(f"AI move computed in {end-start:.2f}s with score: {score}")

                if visualize and graph is not None:
                    p = multiprocessing.Process(target=draw_graph_process, args=(graph, col))
                    p.daemon = True
                    p.start()
                turn = PLAYER

            if is_board_full(board):
                w = check_winner(board)
                if w[PLAYER_PIECE]>w[AI_PIECE]: print("Player wins!")
                elif w[PLAYER_PIECE]<w[AI_PIECE]: print("AI wins!")
                else: print("Draw!")
                pygame.time.wait(3000)
                game_over = True

            clock.tick(30)

if __name__=="__main__":
    multiprocessing.set_start_method('spawn', force=True)
    main()
