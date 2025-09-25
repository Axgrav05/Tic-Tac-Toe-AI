# Game board dimensions and layout
WIDTH = 600
HEIGHT = 600
ROWS = 3
COLS = 3
TILE_SIZE = WIDTH // COLS

# Visual styling constants
LINE_WIDTH = 15
CIRCLE_WIDTH = 15
X_WIDTH = 20
RADIUS = TILE_SIZE // 4
OFFSET = 50

# Color scheme (only used when pygame is available)
BG_COLOR = (28, 170, 156)    # Teal background
LINE_COLOR = (23, 145, 135)  # Darker teal for grid lines
CIRCLE_COLOR = (239, 231, 200)  # Light beige for O
X_COLOR = (66, 66, 66)       # Dark gray for X

# Player constants
EMPTY_CELL = 0
PLAYER_X = 1
PLAYER_O = 2

# Game states
GAME_ONGOING = 0
PLAYER_X_WINS = 1
PLAYER_O_WINS = 2
GAME_DRAW = 3

# AI difficulty levels
AI_RANDOM = 0
AI_MINIMAX = 1


