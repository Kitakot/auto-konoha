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
        self.floorkicks = 0 # number of times the piece has floorkicked, resets when the piece spawns. Used to determine if the piece can still floorkick, and to set lock delay to 0 after the second floorkick.
        '''
        position is the top left corner of the 4x4 mask. The piece will be drawn on the board according to the mask, with the top left corner of the mask at (x, y).
        '''
        self.x = 3
        self.y = 19

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
        self.held_input = {'left': False, 'right': False, 'ccw1': False, 'cw1': False, 'ccw2': False, 'cw2': False, 'soft_drop': False, 'hard_drop': False} # Dictionary to keep track of which controls were held down in the previous frame, used to detect when a key is pressed down or released.

    def check_piece_collision(self, piece, dx=0, dy=0, rotation=0):
        '''
        This method checks if the given piece would collide with the board or other pieces if it were moved by (dx, dy) and rotated by rotation steps.
        It returns True if there would be a collision, and False otherwise.
        '''
        new_orientation = (piece.orientation + rotation) % 4
        new_mask = piece.get_mask(piece.type, new_orientation)
        for py in range(4):
            for px in range(4):
                if new_mask[py][px] == 1:
                    board_x = piece.x + px + dx
                    board_y = piece.y + py + dy
                    if board_x < 0 or board_x >= self.engine.board.width or board_y >= self.engine.board.height:
                        return True # Collision with walls or floor
                    if board_y >= 0 and self.engine.board.grid[board_y][board_x].filled:
                        return True # Collision with filled cells
        return False

    def is_piece_landed(self):
        '''
        This method checks if the current piece has landed. A piece is considered landed if it cannot move down any further without colliding with the board or other pieces.
        '''
        return self.check_piece_collision(self.engine.current_piece, dx=0, dy=1)
    
    def lock_piece(self):
        '''
        This method locks the current piece in place on the board. It should be called when the piece has landed and the lock delay has passed.
        It updates the board grid to fill in the cells occupied by the piece, and then sets the current piece to None to spawn a new piece.
        '''
        piece = self.engine.current_piece
        for py in range(4):
            for px in range(4):
                if piece.mask[py][px] == 1:
                    board_x = piece.x + px
                    board_y = piece.y + py
                    self.engine.board.grid[board_y][board_x].filled = True
                    self.engine.board.grid[board_y][board_x].color = piece.color
        self.engine.current_piece = None
        self.engine.hold_used = False # reset hold usage for the next piece
        self.engine.are_counter = 0 # reset ARE counter to start counting for the next piece

    def check_rotation(self, piece, rotation):
        '''
        This method checks if the given piece can be rotated by rotation steps without colliding with the board or other pieces.
        It returns kick offsets if the rotation is possible, or None if it is not. The kick offsets are a list of (dx, dy) pairs that should be tried in order to see if the piece can be rotated with a kick.
        Kick logic:
        O: No kicks
        L, J, S, Z: 0: (0, 0), 1: (1, 0), 2: (-1, 0)
        T: 0: (0, 0), 1: (1, 0), 2: (-1, 0), 3: (0, -1)
        I: (0, 0), (1, 0), (2, 0), (-1, 0), (0, -1), (0, -2)

        - L, J, and T-pieces, from their 3-wide orientations, will not kick off their center column.
        - The I-piece needs to be touching part of the stack to kick one cell to the right.
        - rotating a T or I-piece after it has floor kicked will permanently set the lock delay for that piece to zero.
        This is actually what prevents the second I floorkick. After the second rotation is processed, movement gets processed, allowing a shift of one cell left or right if it's done fast enough.
        Gravity is then applied. If the I-piece is not in contact with an occupied cell below after processing gravity, any attempt to floorkick will fail.
        If contact does exist, the piece will instantly lock down, preventing rotation from being processed at all.
        '''
        if not self.check_piece_collision(piece, dx=0, dy=0, rotation=rotation):
            return (0, 0) # No kick, just a normal rotation
        if piece.type == 6: # O-piece, no kicks
            return None
        elif piece.type in [1, 2, 3, 4, 5]: # T, L, J, S, Z
            for dx in [1, -1]: # Try kicks of 1 cell to the right and left
                if not self.check_piece_collision(piece, dx=dx, dy=0, rotation=rotation):
                    if piece.type in [1, 2, 3] and piece.orientation % 2 == 0 and self.check_center_column(piece, rotation): # from 3-wide to 2-wide, no kick off center column
                            continue
                    return (dx, 0) # Kick by dx cells horizontally
            if piece.type == 1 and (piece.orientation + rotation) % 4 == 2 and piece.floorkicks == 0 and self.check_piece_collision(piece, dx=0, dy=1) and not self.check_piece_collision(piece, dx=0, dy=-1, rotation=rotation): # T-piece, rotating flat side down, try floor kick if the piece is touching the stack and hasn't floorkicked yet
                piece.floorkicks += 1
                return (0, -1) # Kick by 1 cell upwards
            return None # Rotation not possible
        else: # I-piece
            if (piece.orientation + rotation) % 2 == 0 and (self.check_piece_collision(piece, dx=-1, dy=0) or self.check_piece_collision(piece, dx=1, dy=0)): # from 1 wide to 4-wide, needs to be touching stack to kick
                for dx in [1, 2, -1]:
                    if not self.check_piece_collision(piece, dx=dx, dy=0, rotation=rotation):
                        return (dx, 0) # Horizontal kick by dx cells
            elif (piece.orientation + rotation) % 2 == 1 and self.check_piece_collision(piece, dx=0, dy=1) and piece.floorkicks == 0: # needs to be touching stack to floor kick
                for dy in[-1, -2]:
                    if not self.check_piece_collision(piece, dx=0, dy=dy, rotation=rotation):
                        piece.floorkicks = 1
                        return (0, dy) # Floor kick by dy cells
        return None # Rotation not possible                    

    def check_center_column(self, piece, rotation=0):
        new_orientation = (piece.orientation + rotation) % 4
        new_mask = piece.get_mask(piece.type, new_orientation)
        for dy in range(0, 3):
            for dx in range(0, 3):
                if ((piece.y + dy >= self.engine.board.height or piece.x + dx < 0 or piece.x + dx >= self.engine.board.width) or self.engine.board.grid[piece.y + dy][piece.x + dx].filled) and new_mask[dy][dx] == 1:
                    if dx == 1: # center column
                        return True
                    else:
                        return False
        return False

    def get_input(self):
        '''
        This method handles user input. It serializes the current state of the controls (which keys are pressed) and updates the engine's control variables accordingly.
        Output could be a dictionary like {'left': True, 'right': False, 'ccw1': False, 'cw1': False, 'ccw2': False, 'cw2': False, 'soft_drop': True, 'hard_drop': False, 'hold': False}, which indicates which controls are currently active.
        '''
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        ccw1 = keys[pygame.K_a]
        cw1 = keys[pygame.K_s]
        ccw2 = keys[pygame.K_q]
        cw2 = keys[pygame.K_w]
        soft_drop = keys[pygame.K_DOWN]
        hard_drop = keys[pygame.K_UP]

        return {
            'left': left,
            'right': right,
            'ccw1': ccw1,
            'cw1': cw1,
            'ccw2': ccw2,
            'cw2': cw2,
            'soft_drop': soft_drop,
            'hard_drop': hard_drop
        }

    def update(self):
        '''
        This method updates the game state. It should be called every frame. It updates the engine's state based on the current controls and the passage of time.
        '''
        self.engine.time -= 1
        
        input = self.get_input()

        '''
        Control handling logic:
        Movement: [move] -> [DAS] -> [move] -> [ARR] -> [move] -> [ARR] -> repeat [move] and [ARR]
        Rotation: Immediate on key pressed down, no effect on holding down.
        Hold: Immediate on key pressed down, no effect on holding down. Cannot be used again until the next piece spawns.
        Soft drop: While held down, increases gravity by 1G. Locks the piece in place immediately when it lands.
        Sonic Drop: Immediate on key pressed down, drops the piece to the lowest possible position instantly. Does not lock the piece in place. no effect on holding down.
        '''
        if self.engine.current_piece is not None:
            if input is not None:
                if input['ccw1'] and not self.held_input['ccw1']:
                    kick = self.check_rotation(self.engine.current_piece, rotation=-1)
                    if kick is not None:
                        self.engine.current_piece.orientation = (self.engine.current_piece.orientation - 1) % 4
                        self.engine.current_piece.mask = self.engine.current_piece.get_mask(self.engine.current_piece.type, self.engine.current_piece.orientation)
                        self.engine.current_piece.x += kick[0]
                        self.engine.current_piece.y += kick[1]
                elif input['cw1'] and not self.held_input['cw1']:
                    kick = self.check_rotation(self.engine.current_piece, rotation=1)
                    if kick is not None:
                        self.engine.current_piece.orientation = (self.engine.current_piece.orientation + 1) % 4
                        self.engine.current_piece.mask = self.engine.current_piece.get_mask(self.engine.current_piece.type, self.engine.current_piece.orientation)
                        self.engine.current_piece.x += kick[0]
                        self.engine.current_piece.y += kick[1]

                if input['ccw2'] and not self.held_input['ccw2']:
                    kick = self.check_rotation(self.engine.current_piece, rotation=-1)
                    if kick is not None:
                        self.engine.current_piece.orientation = (self.engine.current_piece.orientation - 1) % 4
                        self.engine.current_piece.mask = self.engine.current_piece.get_mask(self.engine.current_piece.type, self.engine.current_piece.orientation)
                        self.engine.current_piece.x += kick[0]
                        self.engine.current_piece.y += kick[1]

                elif input['cw2'] and not self.held_input['cw2']:
                    kick = self.check_rotation(self.engine.current_piece, rotation=1)
                    if kick is not None:
                        self.engine.current_piece.orientation = (self.engine.current_piece.orientation + 1) % 4
                        self.engine.current_piece.mask = self.engine.current_piece.get_mask(self.engine.current_piece.type, self.engine.current_piece.orientation)
                        self.engine.current_piece.x += kick[0]
                        self.engine.current_piece.y += kick[1]

                if input['right']:
                    if not self.held_input['right']:
                        if not self.check_piece_collision(self.engine.current_piece, dx=1):
                            self.engine.current_piece.x += 1
                    else:
                        self.engine.das_counter += 1
                        if self.engine.das_counter >= self.engine.das:
                            self.engine.arr_counter += 1
                            if self.engine.arr_counter >= self.engine.arr:
                                if not self.check_piece_collision(self.engine.current_piece, dx=1):
                                    self.engine.current_piece.x += 1
                                self.engine.arr_counter = 0 
                elif input['left']:
                    if not self.held_input['left']:
                        if not self.check_piece_collision(self.engine.current_piece, dx=-1):
                            self.engine.current_piece.x -= 1
                    else:
                        self.engine.das_counter += 1
                        if self.engine.das_counter >= self.engine.das:
                            self.engine.arr_counter += 1
                            if self.engine.arr_counter >= self.engine.arr:
                                if not self.check_piece_collision(self.engine.current_piece, dx=-1):
                                    self.engine.current_piece.x -= 1
                                self.engine.arr_counter = 0
                else:
                    self.engine.das_counter = 0
                    self.engine.arr_counter = 0

                if input['soft_drop']:
                    self.engine.gravity_counter += 1 # increase gravity counter by 1 for each frame soft
                    if self.engine.current_piece is not None and self.is_piece_landed():
                        self.lock_piece() # set lock delay counter to max to lock the piece immediately
                if input['hard_drop'] and not self.held_input['hard_drop']:
                    while self.engine.current_piece is not None and not self.is_piece_landed():
                        self.engine.current_piece.y += 1
        else:
            self.engine.are_counter += 1
            self.engine.gravity_counter = 0
            if self.engine.are_counter >= self.engine.are:
                self.engine.are_counter = 0
                self.engine.current_piece = Piece(random.randint(0, 6))

        self.held_input = input

        self.engine.gravity_counter += self.engine.gravity

        if self.engine.current_piece is not None and self.is_piece_landed():
            self.engine.lock_delay_counter += 1
            self.engine.gravity_counter = 0 # reset gravity counter when piece lands
            if self.engine.lock_delay_counter >= self.engine.lock_delay:
                self.engine.lock_delay_counter = 0
                self.lock_piece()
                pass

        while self.engine.gravity_counter >= 1 and self.engine.current_piece is not None and not self.is_piece_landed():
            self.engine.gravity_counter -= 1
            self.engine.current_piece.y += 1
            self.engine.lock_delay_counter = 0 # reset lock delay counter when piece falls (step reset)
            if self.is_piece_landed() and self.engine.current_piece.floorkicks >= 2:
                self.lock_piece() # if the piece has floorkicked twice, it cannot be saved from locking by further floorkicks, so it locks immediately upon landing regardless of lock delay


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