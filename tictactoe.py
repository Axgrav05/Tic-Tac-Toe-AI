import sys
import random
import copy
from typing import Tuple, List, Optional, Union

# Import pygame conditionally to allow testing without it
try:
    import pygame
    import numpy as np
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Running in test mode.")

from constants import *

# Initialize Pygame only if available
if PYGAME_AVAILABLE:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tic-Tac-Toe AI Game')
    screen.fill(BG_COLOR)
else:
    screen = None


class Board:
    """
    Represents the tic-tac-toe game board and handles game state logic.

    The board uses a 3x3 numpy array where:
    - 0 represents an empty cell
    - 1 represents Player X
    - 2 represents Player O
    """

    def __init__(self):
        """Initialize an empty 3x3 game board."""
        if PYGAME_AVAILABLE:
            self.tiles = np.zeros((ROWS, COLS), dtype=int)
        else:
            # Fallback to nested lists when numpy is not available
            self.tiles = [[EMPTY_CELL for _ in range(COLS)] for _ in range(ROWS)]
        self.marked_tiles = 0

    def get_winner(self) -> int:
        """
        Check if there's a winner on the board.

        Returns:
            0 if no winner yet
            1 if Player X wins
            2 if Player O wins
        """
        # Check vertical wins
        for col in range(COLS):
            if (self.tiles[0][col] == self.tiles[1][col] == self.tiles[2][col] != EMPTY_CELL):
                return int(self.tiles[0][col])

        # Check horizontal wins
        for row in range(ROWS):
            if (self.tiles[row][0] == self.tiles[row][1] == self.tiles[row][2] != EMPTY_CELL):
                return int(self.tiles[row][0])

        # Check descending diagonal (top-left to bottom-right)
        if (self.tiles[0][0] == self.tiles[1][1] == self.tiles[2][2] != EMPTY_CELL):
            return int(self.tiles[1][1])

        # Check ascending diagonal (bottom-left to top-right)
        if (self.tiles[2][0] == self.tiles[1][1] == self.tiles[0][2] != EMPTY_CELL):
            return int(self.tiles[1][1])

        return GAME_ONGOING

    def get_winning_line(self) -> Optional[Tuple[str, int]]:
        """
        Get the winning line type and index if there's a winner.

        Returns:
            Tuple of (line_type, index) where line_type is 'row', 'col', or 'diag'
            None if no winner
        """
        # Check vertical wins
        for col in range(COLS):
            if (self.tiles[0][col] == self.tiles[1][col] == self.tiles[2][col] != EMPTY_CELL):
                return ('col', col)

        # Check horizontal wins
        for row in range(ROWS):
            if (self.tiles[row][0] == self.tiles[row][1] == self.tiles[row][2] != EMPTY_CELL):
                return ('row', row)

        # Check descending diagonal
        if (self.tiles[0][0] == self.tiles[1][1] == self.tiles[2][2] != EMPTY_CELL):
            return ('diag', 0)  # 0 for descending diagonal

        # Check ascending diagonal
        if (self.tiles[2][0] == self.tiles[1][1] == self.tiles[0][2] != EMPTY_CELL):
            return ('diag', 1)  # 1 for ascending diagonal

        return None


    def mark_tile(self, row: int, col: int, player: int) -> bool:
        """
        Mark a tile with the specified player's symbol.

        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            player: Player number (1 for X, 2 for O)

        Returns:
            True if move was successful, False if tile was already occupied
        """
        if not self.is_valid_position(row, col) or not self.is_empty_tile(row, col):
            return False

        self.tiles[row][col] = player
        self.marked_tiles += 1
        return True

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if the given position is within board bounds."""
        return 0 <= row < ROWS and 0 <= col < COLS

    def is_empty_tile(self, row: int, col: int) -> bool:
        """Check if a tile is empty (unoccupied)."""
        return self.is_valid_position(row, col) and self.tiles[row][col] == EMPTY_CELL

    def get_empty_tiles(self) -> List[Tuple[int, int]]:
        """Get a list of all empty tile positions."""
        empty_tiles = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.is_empty_tile(row, col):
                    empty_tiles.append((row, col))
        return empty_tiles

    def is_full(self) -> bool:
        """Check if the board is completely filled."""
        return self.marked_tiles == ROWS * COLS

    def is_empty(self) -> bool:
        """Check if the board has no moves made yet."""
        return self.marked_tiles == 0

    def copy(self) -> 'Board':
        """Create a deep copy of the current board state."""
        new_board = Board()
        if PYGAME_AVAILABLE:
            new_board.tiles = np.copy(self.tiles)
        else:
            # Deep copy for nested lists
            new_board.tiles = [row[:] for row in self.tiles]
        new_board.marked_tiles = self.marked_tiles
        return new_board

class AI:
    """
    AI player that can play tic-tac-toe using different strategies.

    Supports two difficulty levels:
    - Level 0: Random moves
    - Level 1: Minimax algorithm (optimal play)
    """

    def __init__(self, level: int = AI_MINIMAX, player: int = PLAYER_O):
        """
        Initialize the AI player.

        Args:
            level: AI difficulty (0 for random, 1 for minimax)
            player: Player number (1 for X, 2 for O)
        """
        self.level = level
        self.player = player

    def get_random_move(self, board: Board) -> Tuple[int, int]:
        """
        Get a random valid move from available positions.

        Args:
            board: Current game board

        Returns:
            Tuple of (row, col) for the selected move
        """
        empty_tiles = board.get_empty_tiles()
        if not empty_tiles:
            raise ValueError("No empty tiles available")

        return random.choice(empty_tiles)

    def minimax(self, board: Board, maximizing: bool) -> Tuple[int, Optional[Tuple[int, int]]]:
        """
        Minimax algorithm implementation for optimal tic-tac-toe play.

        This algorithm recursively evaluates all possible game states to find
        the optimal move. It assumes both players play perfectly.

        Args:
            board: Current game board state
            maximizing: True if maximizing player's turn (Player X), False for minimizing (Player O)

        Returns:
            Tuple of (evaluation_score, best_move)
            - evaluation_score: 1 if X wins, -1 if O wins, 0 for draw
            - best_move: (row, col) tuple for optimal move, None if game over
        """
        winner = board.get_winner()

        # Base cases: game is over
        if winner == PLAYER_X:
            return 1, None  # X wins (good for maximizing player)
        elif winner == PLAYER_O:
            return -1, None  # O wins (good for minimizing player)
        elif board.is_full():
            return 0, None  # Draw

        empty_tiles = board.get_empty_tiles()
        best_move = None

        if maximizing:
            # Maximizing player (X) wants the highest score
            max_eval = float('-inf')

            for row, col in empty_tiles:
                # Try this move
                temp_board = board.copy()
                temp_board.mark_tile(row, col, PLAYER_X)

                # Recursively evaluate this position
                eval_score, _ = self.minimax(temp_board, False)

                # Update best move if this is better
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (row, col)

            return max_eval, best_move
        else:
            # Minimizing player (O) wants the lowest score
            min_eval = float('inf')

            for row, col in empty_tiles:
                # Try this move
                temp_board = board.copy()
                temp_board.mark_tile(row, col, self.player)

                # Recursively evaluate this position
                eval_score, _ = self.minimax(temp_board, True)

                # Update best move if this is better
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (row, col)

            return min_eval, best_move

    def get_best_move(self, board: Board) -> Tuple[int, int]:
        """
        Get the best move for the current board state based on AI level.

        Args:
            board: Current game board

        Returns:
            Tuple of (row, col) for the selected move
        """
        if self.level == AI_RANDOM:
            move = self.get_random_move(board)
            print(f'AI (Level {self.level}) chose random move: {move}')
            return move
        else:
            # Use minimax algorithm
            evaluation, move = self.minimax(board, False)
            print(f'AI (Level {self.level}) chose move: {move} with evaluation: {evaluation}')

            if move is None:
                # Fallback to random move if minimax fails
                move = self.get_random_move(board)

            return move
    
class GameRenderer:
    """
    Handles all pygame rendering for the tic-tac-toe game.
    Separates UI concerns from game logic.
    """

    def __init__(self, screen):
        if screen is None:
            raise ValueError("Screen is required for GameRenderer")
        self.screen = screen

    def draw_grid(self):
        """Draw the tic-tac-toe grid lines."""
        self.screen.fill(BG_COLOR)

        # Vertical grid lines
        pygame.draw.line(self.screen, LINE_COLOR,
                        (TILE_SIZE, 0), (TILE_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(self.screen, LINE_COLOR,
                        (WIDTH - TILE_SIZE, 0), (WIDTH - TILE_SIZE, HEIGHT), LINE_WIDTH)

        # Horizontal grid lines
        pygame.draw.line(self.screen, LINE_COLOR,
                        (0, TILE_SIZE), (WIDTH, TILE_SIZE), LINE_WIDTH)
        pygame.draw.line(self.screen, LINE_COLOR,
                        (0, HEIGHT - TILE_SIZE), (WIDTH, HEIGHT - TILE_SIZE), LINE_WIDTH)

    def draw_x(self, row: int, col: int):
        """Draw an X symbol at the specified grid position."""
        # Calculate position within the tile
        start_desc = (col * TILE_SIZE + OFFSET, row * TILE_SIZE + OFFSET)
        end_desc = (col * TILE_SIZE + TILE_SIZE - OFFSET, row * TILE_SIZE + TILE_SIZE - OFFSET)
        start_asc = (col * TILE_SIZE + OFFSET, row * TILE_SIZE + TILE_SIZE - OFFSET)
        end_asc = (col * TILE_SIZE + TILE_SIZE - OFFSET, row * TILE_SIZE + OFFSET)

        # Draw both diagonal lines of the X
        pygame.draw.line(self.screen, X_COLOR, start_desc, end_desc, X_WIDTH)
        pygame.draw.line(self.screen, X_COLOR, start_asc, end_asc, X_WIDTH)

    def draw_o(self, row: int, col: int):
        """Draw an O symbol at the specified grid position."""
        center_pos = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
        pygame.draw.circle(self.screen, CIRCLE_COLOR, center_pos, RADIUS, CIRCLE_WIDTH)

    def draw_figure(self, row: int, col: int, player: int):
        """Draw the appropriate figure (X or O) for the given player."""
        if player == PLAYER_X:
            self.draw_x(row, col)
        elif player == PLAYER_O:
            self.draw_o(row, col)

    def draw_winning_line(self, line_type: str, index: int, winner: int):
        """Draw a line through the winning combination."""
        color = CIRCLE_COLOR if winner == PLAYER_O else X_COLOR

        if line_type == 'col':
            # Vertical winning line
            start_pos = (index * TILE_SIZE + TILE_SIZE // 2, 20)
            end_pos = (index * TILE_SIZE + TILE_SIZE // 2, HEIGHT - 20)
        elif line_type == 'row':
            # Horizontal winning line
            start_pos = (20, index * TILE_SIZE + TILE_SIZE // 2)
            end_pos = (WIDTH - 20, index * TILE_SIZE + TILE_SIZE // 2)
        elif line_type == 'diag' and index == 0:
            # Descending diagonal (top-left to bottom-right)
            start_pos = (20, 20)
            end_pos = (WIDTH - 20, HEIGHT - 20)
        else:
            # Ascending diagonal (bottom-left to top-right)
            start_pos = (20, HEIGHT - 20)
            end_pos = (WIDTH - 20, 20)

        pygame.draw.line(self.screen, color, start_pos, end_pos, LINE_WIDTH)


class Game:
    """
    Main game controller that manages game state and coordinates between
    the board, AI, and renderer components.
    """

    def __init__(self, screen):
        """Initialize a new game instance."""
        self.board = Board()
        self.ai = AI()
        self.renderer = GameRenderer(screen)
        self.current_player = PLAYER_X
        self.game_mode = 'ai'  # 'ai' or 'pvp'
        self.is_running = True
        self.game_over = False
        self.renderer.draw_grid()

    def make_move(self, row: int, col: int) -> bool:
        """
        Attempt to make a move at the specified position.

        Args:
            row: Row index (0-2)
            col: Column index (0-2)

        Returns:
            True if move was successful, False otherwise
        """
        if self.game_over or not self.board.mark_tile(row, col, self.current_player):
            return False

        self.renderer.draw_figure(row, col, self.current_player)

        # Check for game end conditions
        winner = self.board.get_winner()
        if winner != GAME_ONGOING:
            self._handle_game_end(winner)
        elif self.board.is_full():
            self._handle_game_end(GAME_DRAW)
        else:
            self._next_turn()

        return True

    def _handle_game_end(self, result: int):
        """Handle end of game logic."""
        self.game_over = True
        self.is_running = False

        if result in [PLAYER_X_WINS, PLAYER_O_WINS]:
            # Draw winning line
            winning_line = self.board.get_winning_line()
            if winning_line:
                line_type, index = winning_line
                self.renderer.draw_winning_line(line_type, index, result)

        # Print game result
        if result == PLAYER_X_WINS:
            print("Player X wins!")
        elif result == PLAYER_O_WINS:
            print("Player O wins!")
        else:
            print("Game is a draw!")

    def _next_turn(self):
        """Switch to the next player's turn."""
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def toggle_game_mode(self):
        """Toggle between AI and player-vs-player modes."""
        self.game_mode = 'pvp' if self.game_mode == 'ai' else 'ai'
        print(f"Game mode switched to: {self.game_mode}")

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self.game_over

    def reset(self):
        """Reset the game to initial state."""
        self.board = Board()
        self.current_player = PLAYER_X
        self.is_running = True
        self.game_over = False
        self.renderer.draw_grid()
        print("Game reset!")

    def should_ai_move(self) -> bool:
        """Check if it's the AI's turn to move."""
        return (self.game_mode == 'ai' and
                self.current_player == self.ai.player and
                self.is_running and
                not self.game_over)


    


def main():
    """
    Main game loop that handles events and coordinates game flow.

    Controls:
    - Mouse click: Make a move
    - G key: Toggle game mode (AI vs PvP)
    - R key: Reset game
    - 0 key: Set AI to random difficulty
    - 1 key: Set AI to minimax difficulty
    - ESC/Close: Exit game
    """
    if not PYGAME_AVAILABLE:
        print("Error: pygame is required to run the game. Please install pygame.")
        print("You can run 'pip install pygame numpy' to install the required dependencies.")
        return

    # Initialize game components
    game = Game(screen)

    print("Tic-Tac-Toe AI Game Started!")
    print("Controls:")
    print("  - Click to make a move")
    print("  - G: Toggle game mode (AI/PvP)")
    print("  - R: Reset game")
    print("  - 0: AI Random mode")
    print("  - 1: AI Minimax mode")
    print("  - ESC: Exit")

    clock = pygame.time.Clock()

    # Main game loop
    while True:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_g:
                    game.toggle_game_mode()
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_0:
                    game.ai.level = AI_RANDOM
                    print(f"AI difficulty set to: Random")
                elif event.key == pygame.K_1:
                    game.ai.level = AI_MINIMAX
                    print(f"AI difficulty set to: Minimax")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks for player moves
                if not game.is_game_over():
                    mouse_pos = event.pos
                    row = mouse_pos[1] // TILE_SIZE
                    col = mouse_pos[0] // TILE_SIZE

                    # Attempt to make the move
                    if game.board.is_valid_position(row, col):
                        success = game.make_move(row, col)
                        if not success:
                            print(f"Invalid move: position ({row}, {col}) is already occupied")

        # Handle AI moves
        if game.should_ai_move():
            try:
                row, col = game.ai.get_best_move(game.board)
                game.make_move(row, col)
            except Exception as e:
                print(f"AI move error: {e}")
                # Reset game on AI error to prevent infinite loops
                game.reset()

        # Update display
        pygame.display.update()
        clock.tick(60)  # Limit to 60 FPS


if __name__ == "__main__":
    main()