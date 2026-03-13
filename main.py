import pygame
import random

'''
This is an application that replicates the Konoha mode from T****s the Grand Master 4 (TGM Rule).

'''

class Engine:
    def __init__(self):
        self.board = Board()
        self.current_piece = None
        self.next_piece = None
        self.hold_piece = None
        self.hold_used = False # Whether the player has used their hold for the current piece, resets when a new piece spawns.
        self.level = 0 # Current level, determines the speed of the pieces. Increases after each piece placed and line clear.
        self.lines_cleared = 0
        self.all_clears = 0 # Number of times the player has cleared the board completely.
        self.time = 0 # Time left in the current level, in frames. When it reaches 0, the player loses.
        self.big_mode = False # Big mode, when true, the pieces are 2x2 blocks instead of 1x1 blocks.

        '''
        Control Handling
        '''
        self.das = 18 # Delayed Auto Shift, how many frames to wait before moving the piece again when holding down a key
        self.das_counter = 0 # Counter for DAS, counts how many frames the key has been held down

        self.arr = 1 # Auto Repeat Rate, how many frames to wait between moving the piece when holding down a key after the initial DAS delay
        self.arr_counter = 0 # Counter for ARR, counts how many frames since the last move when holding down a key after the initial DAS delay

        self.are = 27 # ARE, how many frames to wait after a piece is placed before the next piece spawns
        self.are_counter = 0 # Counter for ARE, counts how many frames since the last piece was placed

        self.line_are = 25 # Line ARE, how many frames to wait after a line is cleared before the next piece spawns
        self.line_are_counter = 0 # Counter for Line ARE, counts how many frames since the last line was cleared

        self.lock_delay = 60 # Lock delay, how many frames to wait before locking the piece in place after it has landed
        self.lock_delay_counter = 0 # Counter for lock delay, counts how many frames since the piece has landed

        self.gravity = 4/256 # Gravity, measured in cells per frame (G). Determines how fast the piece falls. Increases with level. Caps at 21G.
        self.gravity_counter = 0 # Counter for gravity, counts the accumulated gavity in cells. When it reaches 1, the piece falls by one cell and the counter resets.

class Board:
    '''
    This class represents the game board. It has a grid of minos and methods to manipulate the board.
    '''
    def __init__(self):
        self.width = 10
        self.height = 40
        self.grid = [[Mino() for _ in range(self.width)] for _ in range(self.height)]

class Piece:
    '''
    This class represents a piece in the game. It has a shape and a position on the board.
    '''
    def __init__(self, type):
        '''
        type: 0 = I, 1 = T, 2 = L, 3 = J, 4 = S, 5 = Z, 6 = O
        orientation: 0 = spawn, 1 = right, 2 = reverse, 3 = left
        '''
        self.type = type
        self.mask = self.get_mask(type, orientation=0)
        self.orientation = 0
        self.color = self.get_color()
        '''
        position is the top left corner of the 4x4 mask. The piece will be drawn on the board according to the mask, with the top left corner of the mask at (x, y).
        '''
        self.x = 3
        self.y = 19 #spawn on 21-22nd row, but we want to be able to see the piece when it spawns

    def get_mask(self, type, orientation):
        if type == 0: #I
            if orientation % 2 == 0:
                return [[0, 0, 0, 0],
                        [1, 1, 1, 1],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0]]
            else:
                return [[0, 0, 1, 0],
                        [0, 0, 1, 0],
                        [0, 0, 1, 0],
                        [0, 0, 1, 0]]
        elif type == 1: #T
            if orientation == 0:
                return [[0, 0, 0, 0],
                        [1, 1, 1, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 0]]
            elif orientation == 1:
                return [[0, 1, 0, 0],
                        [1, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 0]]
            elif orientation == 2:
                return [[0, 0, 0, 0],
                        [0, 1, 0, 0],
                        [1, 1, 1, 0],
                        [0, 0, 0, 0]]
            else:
                return [[0, 1, 0, 0],
                        [0, 1, 1, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 0]]
        elif type == 2: #L
            if orientation == 0:
                return [[0, 0, 0, 0],
                        [1, 1, 1, 0],
                        [1, 0, 0, 0],
                        [0, 0, 0, 0]]
            elif orientation == 1:
                return [[1, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 0]]
            elif orientation == 2:
                return [[0, 0, 0, 0],
                        [0, 0, 1, 0],
                        [1, 1, 1, 0],
                        [0, 0, 0, 0]]
            else:
                return [[0, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 1, 1, 0],
                        [0, 0, 0, 0]]
        elif type == 3: #J
            if orientation == 0:
                return [[0, 0, 0, 0],
                        [1, 1, 1, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 0]]
            elif orientation == 1:
                return [[0, 1, 0, 0],
                        [0, 1, 0, 0],
                        [1, 1, 0, 0],
                        [0, 0, 0, 0]]
            elif orientation == 2:
                return [[0, 0, 0, 0],
                        [1, 0, 0, 0],
                        [1, 1, 1, 0],
                        [0, 0, 0, 0]]
            else:
                return [[0, 1, 1, 0],
                        [0, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 0]]
        elif type == 4: #S
            if orientation % 2 == 0:
                return [[0, 0, 0, 0],
                        [0, 1, 1, 0],
                        [1, 1, 0, 0],
                        [0, 0, 0, 0]]
            else:
                return [[1, 0, 0, 0],
                        [1, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 0]]
        elif type == 5: #Z
            if orientation % 2 == 0:
                return [[0, 0, 0, 0],
                        [1, 1, 0, 0],
                        [0, 1, 1, 0],
                        [0, 0, 0, 0]]
            else:
                return [[0, 1, 0, 0],
                        [1, 1, 0, 0],
                        [1, 0, 0, 0],
                        [0, 0, 0, 0]]
        else: #O
            return [[0, 0, 0, 0],
                    [0, 1, 1, 0],
                    [0, 1, 1, 0],
                    [0, 0, 0, 0]]

    def get_color(self):
        colors = [pygame.Color('red'),
                  pygame.Color('cyan'),
                  pygame.Color('orange'),
                  pygame.Color('blue'),
                  pygame.Color('magenta'),
                  pygame.Color('green'),
                  pygame.Color('yellow')]
        return colors[self.type]

class Mino:
    '''
    This class represents a single square in the game. It has a position and a color.
    '''
    def __init__(self):
        self.filled = False
        self.color = pygame.Color('black')

class Game:
    '''
    This class represents the game itself. It has an engine and methods to run the game loop and handle input.
    '''
    def __init__(self):
        self.engine = Engine()

    def get_input(self):
        '''
        This method handles user input. It serializes the current state of the controls (which keys are pressed) and updates the engine's control variables accordingly.
        Output could be a dictionary like {'left': True, 'right': False, 'rotate': False, 'soft_drop': True, 'hard_drop': False, 'hold': False}, which indicates which controls are currently active.
        '''
        pass

    def update(self):
        '''
        This method updates the game state. It should be called every frame. It updates the engine's state based on the current controls and the passage of time.
        '''
        self.engine.time -= 1
        
        input = self.get_input()

        # Update engine state based on input and time passage here
        if self.engine.current_piece is not None:
            # Handle piece movement, rotation, gravity, lock delay, ARE, line clears, etc. here
            pass

        self.engine.gravity_counter += self.engine.gravity
        while self.engine.gravity_counter >= 1:
            self.engine.gravity_counter -= 1
            self.engine.current_piece.y += 1
            # Move piece down by one cell here


class Renderer:
    '''
    This class is responsible for drawing the game on the screen. It has a method to draw the board and pieces.
    '''
    def __init__(self, screen):
        self.screen = screen
        self.engine = None
    
    def draw_board(self, board):
        for y in range(board.height):
            for x in range(board.width):
                mino = board.grid[y][x]
                if mino.filled:
                    pygame.draw.rect(self.screen, mino.color, (x * 16 + HORIZONATAL_OFFSET, y * 16 + VERTICAL_OFFSET, 16, 16))
                if self.is_piece_at(x, y):
                    piece = self.engine.current_piece
                    pygame.draw.rect(self.screen, piece.color, (x * 16 + HORIZONATAL_OFFSET, y * 16 + VERTICAL_OFFSET, 16, 16))
                elif (y >= 20): # only draw grid lines for the visible part of the board
                    pygame.draw.rect(self.screen, pygame.Color('lightgray'), (x * 16 + HORIZONATAL_OFFSET, y * 16 + VERTICAL_OFFSET, 16, 16), 1)

    def is_piece_at(self, x, y):
        if self.engine.current_piece is None:
            return False
        piece = self.engine.current_piece
        for py in range(4):
            for px in range(4):
                if piece.mask[py][px] == 1:
                    if piece.x + px == x and piece.y + py == y:
                        return True
        return False

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
HORIZONATAL_OFFSET = (WIDTH - 10 * 16) // 2
VERTICAL_OFFSET = -(20 * 16) + (HEIGHT - 20 * 16) // 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto-Konoha")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

game = Game()
renderer = Renderer(screen)
renderer.engine = game.engine
game.engine.current_piece = Piece(random.randint(0, 6))  # test piece

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    game.update()

    screen.fill((255, 255, 255))  # Clear the screen with white background
    
    # Draw the game elements
    renderer.draw_board(game.engine.board)
    
    # Update display
    pygame.display.flip()

pygame.quit()