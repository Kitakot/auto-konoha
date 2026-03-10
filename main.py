import pygame

'''
This is an application that replicates the Konoha mode from T****s the Grand Master 4 (TGM Rule).

'''

class Engine:
    def __init__(self):
        pass

class Board:
    '''
    This class represents the game board. It has a grid of minos and methods to manipulate the board.
    '''
    def __init__(self):
        self.width = 5
        self.height = 10
        self.hidden_rows = 10
        self.grid = [[Mino() for _ in range(self.width)] for _ in range(self.height + self.hidden_rows)]

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


class Mino:
    '''
    This class represents a single square in the game. It has a position and a color.
    '''
    def __init__(self):
        self.filled = False

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto-Konoha")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill screen with color
    screen.fill((0, 0, 0))
    
    # Update display
    pygame.display.flip()

pygame.quit()