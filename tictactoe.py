import sys
import pygame
import random
import copy
import numpy as np

from constants import *

# PYGAME Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('TicTacToe Against AI Player')
screen.fill(BG_COLOR)


class Board:
    
    def __init__(self):
        self.tiles = np.zeros((ROWS,COLS))
        self.empty_tiles = self.tiles
        self.marked_tiles = 0

    def final_state(self, show = False):
        # return 0 if no win yet, 1 if player 1 wins, 2 if player 2 wins

        # Vertical Wins
        for col in range(COLS):
            if self.tiles[0][col] == self.tiles[1][col] == self.tiles[2][col] != 0:
                if show:
                    color = CIRCLE_COLOR if self.tiles[0][col] == 2 else X_COLOR
                    initial_pos = (col * TILE_SIZE + TILE_SIZE // 2, 20)
                    final_pos = (col * TILE_SIZE + TILE_SIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, initial_pos, final_pos, LINE_WIDTH)
                return self.tiles[0][col]
            
        # Horizontal Wins
        for row in range(ROWS):
            if self.tiles[row][0] == self.tiles[row][1] == self.tiles[row][2] != 0:
                if show:
                    color = CIRCLE_COLOR if self.tiles[row][0] == 2 else X_COLOR
                    initial_pos = (20, row * TILE_SIZE + TILE_SIZE // 2)
                    final_pos = (WIDTH - 20, row * TILE_SIZE + TILE_SIZE // 2)
                    pygame.draw.line(screen, color, initial_pos, final_pos, LINE_WIDTH)
                return self.tiles[row][0]
    
        # Descending Diagonal Wins
        if self.tiles[0][0] == self.tiles[1][1] == self.tiles [2][2] != 0:
            if show:
                    color = CIRCLE_COLOR if self.tiles[1][1] == 2 else X_COLOR
                    initial_pos = (20, 20)
                    final_pos = (WIDTH - 20, HEIGHT - 20)
                    pygame.draw.line(screen, color, initial_pos, final_pos, X_WIDTH)
            return self.tiles[1][1]
            
        # Ascending Diagonal Wins
        if self.tiles[2][0] == self.tiles[1][1] == self.tiles[0][2] != 0:
            if show:
                    color = CIRCLE_COLOR if self.tiles[1][1] == 2 else X_COLOR
                    initial_pos = (20, HEIGHT - 20)
                    final_pos = (WIDTH - 20, HEIGHT - 20)
                    pygame.draw.line(screen, color, initial_pos, final_pos, X_WIDTH)
            return self.tiles[1][1]
        
        return 0


    def mark_tile(self, row, col, player):
        self.tiles[row][col] = player
        self.marked_tiles += 1

    def check_empty_tile(self, row, col):
        return self.tiles[row][col] == 0
    
    def get_empty_tiles(self):
        empty_tiles = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.check_empty_tile(row, col):
                    empty_tiles.append((row,col))
        return empty_tiles
    
    def isfull(self):
        return self.marked_tiles == 9
    
    def isempty(self):
        return self.marked_tiles == 0

class AI:

    def __init__(self, level = 1, player = 2):
        self.level = level
        self.player = player

    def rnd(self, board):
        empty_tiles = board.get_empty_tiles()
        idx = random.randrange(0, len(empty_tiles))

        return empty_tiles[idx]
    
    def minimax(self, board, maximizing):
        # Base Case
        case = board.final_state()

        # Player 1 Wins
        if case == 1:
            return 1, None
        
        # Player 2 Wins
        if case == 2:
            return -1, None
        
        # Draw
        elif board.isfull():
            return 0, None
        
        if maximizing:
            max_eval = -100
            best_move = None
            empty_tiles = board.get_empty_tiles()

            for (row, col) in empty_tiles:
                temp_board = copy.deepcopy(board)
                temp_board.mark_tile(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_tiles = board.get_empty_tiles()

            for (row, col) in empty_tiles:
                temp_board = copy.deepcopy(board)
                temp_board.mark_tile(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move
            
    def eval(self, main_board):
        if self.level == 0:
            # Random Choice
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # Minimax Algorithm Based Choice
            eval, move = self.minimax(main_board, False)
        print(f'AI has chosen to mark the square in pos {move} with an eval of : {eval}')
        return move
    
class Game:

    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1
        self.gamemode = 'ai' # pvp or ai
        self.running = True
        self.show_gameboard_lines()

    def show_gameboard_lines(self):
        screen.fill(BG_COLOR)
        # Vertical GameBoard Lines
        pygame.draw.line(screen, LINE_COLOR, (TILE_SIZE, 0), (TILE_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH-TILE_SIZE, 0), (WIDTH-TILE_SIZE, HEIGHT), LINE_WIDTH)

        # Horizontal GameBoard Lines
        pygame.draw.line(screen, LINE_COLOR, (0, TILE_SIZE), (WIDTH, TILE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT-TILE_SIZE), (WIDTH, HEIGHT-TILE_SIZE), LINE_WIDTH)

    def draw_figure(self, row, col):
        # Player 1 plays an X and Player 2 plays an O
        if self.player == 1:
            # Draw an X
                # Left Slash
                start_desc = (col * TILE_SIZE + OFFSET, row * TILE_SIZE + OFFSET)
                end_desc = (col * TILE_SIZE + TILE_SIZE - OFFSET, row * TILE_SIZE + TILE_SIZE - OFFSET)
                pygame.draw.line(screen, X_COLOR, start_desc, end_desc, X_WIDTH)

                # Right Slash
                start_asc = (col * TILE_SIZE + OFFSET, row * TILE_SIZE + TILE_SIZE - OFFSET)
                end_asc = (col * TILE_SIZE + TILE_SIZE - OFFSET, row * TILE_SIZE + OFFSET)
                pygame.draw.line(screen, X_COLOR, start_asc, end_asc, X_WIDTH)

        elif self.player == 2:
            # Draw an O
            center_pos = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(screen, CIRCLE_COLOR, center_pos, RADIUS, CIRCLE_WIDTH)

    def make_move(self, row, col):
        self.board.mark_tile(row, col, self.player)
        self.draw_figure(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemmode(self):
        self.gamemode == 'ai' if self.gamemode == 'ai' else 'pvp'

    def isover(self):
        return self.board.final_state(show = True) != 0 or self.board.isfull()

    def reset(self):
        self.__init__()


    


def main():

    # object
    game = Game()
    board = game.board
    ai = game.ai

    # Main Program Loop
    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
 

            if event.type == pygame.KEYDOWN:
                # Press "G" to Change Gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # Press "R" to Restart Gamemode
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai
                
                # Press "0" for Random AI Level 0
                if event.key == pygame.K_0:
                    ai.level = 0

                # Press "1" for Random AI Level 1
                if event.key == pygame.K_1:
                    ai.level = 1
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // TILE_SIZE
                col = pos[0] // TILE_SIZE

                if board.check_empty_tile(row,col) and game.running:
                    game.make_move(row, col)

                    if game.isover():
                        game.running = False

        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            # Update Screen
            pygame.display.update()

            # AI Methods
            row, col = ai.eval(board)
            game.make_move(row, col)

            if game.isover():
                game.running = False


        pygame.display.update()

main()