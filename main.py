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
        self.level = 0
        self.lines_cleared = 0
        self.all_clears = 0

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
        self.y = 17 #spawn on 21-22nd row, but we want to be able to see the piece when it spawns

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
        if self.type == 0: #I
            return pygame.Color('red')
        elif self.type == 1: #T
            return pygame.Color('cyan')
        elif self.type == 2: #L
            return pygame.Color('orange')
        elif self.type == 3: #J
            return pygame.Color('blue')
        elif self.type == 4: #S
            return pygame.Color('purple')
        elif self.type == 5: #Z
            return pygame.Color('green')
        else: #O
            return pygame.Color('yellow')

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

    screen.fill((255, 255, 255))  # Clear the screen with white background
    
    # Draw the game elements
    renderer.draw_board(game.engine.board)
    
    # Update display
    pygame.display.flip()

pygame.quit()