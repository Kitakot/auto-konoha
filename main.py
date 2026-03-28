import pygame
import random

'''
This is an application that replicates the Konoha mode from T****s the Grand Master 4 (TGM Rule).

'''

class Engine:
    def __init__(self):
        self.board = Board()
        self.current_piece = None
        self.next_piece = [None, None, None, None, None, None] # Queue of the next 6 pieces that will spawn, initialized with None to allow any piece to spawn at the start of the game.
        self.hold_piece = None
        self.hold_used = False # Whether the player has used their hold for the current piece, resets when a new piece spawns.
        self.piece_history = [Piece(4), Piece(4), Piece(5), Piece(5)] # History of the last 4 pieces that spawned, used to determine the next pieces that spawn. Initialized with S and Z pieces
        self.level = 0 # Current level, determines the speed of the pieces. Increases after each piece placed and line clear.
        self.lines_cleared = 0
        self.all_clears = 0 # Number of times the player has cleared the board completely.
        self.time = 15000 # Time left in the current level, in frames. When it reaches 0, the player loses.
        self.big_mode = True # Big mode, when true, the pieces are 2x2 blocks instead of 1x1 blocks.
        self.state = 'active' # Game state, can be 'active', 'are' and 'line_are'
        self.lines = [] # Lines that are currently being cleared, used to determine which lines to draw as clearing and which lines to collapse after the line clear delay.

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

        self.time_bonus_base = [1, 2, 5, 11]
        self.all_clear_time_bonus = [300, 480, 660, 900]
        self.hurryup_time_bonus = [0, 0, 0, 60] #time bonus added after level 1000 no matter if it is all clear or not.
        self.level_bonus = [1, 2, 4, 6] # level added for line clears

    def get_time_bonus(self, lines_cleared, all_clear):
        '''
        This method calculates the time bonus for clearing lines. The bonus is added to the timer when lines are cleared, and is based on the number of lines cleared and whether an all clear was achieved.
        '''
        if self.level >= 1000:
            return self.hurryup_time_bonus[lines_cleared - 1]
        else:
            if all_clear:
                return self.all_clear_time_bonus[lines_cleared - 1]
            else:
                return self.time_bonus_base[lines_cleared - 1]
            
    def get_level_bonus(self, lines_cleared):
        '''
        This method calculates the level bonus for clearing lines. The bonus is added to the level when lines are cleared, and is based on the number of lines cleared.
        '''
        return self.level_bonus[lines_cleared - 1]
    
    def update_gravity(self):
        if self.level < 8:
            self.gravity = 4/256
        elif self.level < 19:
            self.gravity = 5/256
        elif self.level < 35:
            self.gravity = 6/256
        elif self.level < 40:
            self.gravity = 8/256
        elif self.level < 50:
            self.gravity = 10/256
        elif self.level < 60:
            self.gravity = 12/256
        elif self.level < 70:
            self.gravity = 16/256
        elif self.level < 80:
            self.gravity = 32/256
        elif self.level < 90:
            self.gravity = 48/256
        elif self.level < 101:
            self.gravity = 64/256
        elif self.level < 112:
            self.gravity = 16/256
        elif self.level < 121:
            self.gravity = 48/256
        elif self.level < 132:
            self.gravity = 80/256
        elif self.level < 144:
            self.gravity = 128/256
        elif self.level < 156:
            self.gravity = 112/256
        elif self.level < 167:
            self.gravity = 144/256
        elif self.level < 177:
            self.gravity = 176/256
        elif self.level < 200:
            self.gravity = 192/256
        else:
            self.gravity = 21
        

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

        for _ in range(6):
            self.generate_next_piece()
            self.engine.next_piece.pop(0)

    def block_scale(self):
        return 2 if self.engine.big_mode else 1

    def horizontal_step(self):
        return 2 if self.engine.big_mode else 1

    def kick_step(self):
        return 2 if self.engine.big_mode else 1

    def generate_next_piece(self):
        for i in range(6): #try to generate a non-duplicate piece 6 times.
            next_piece_type = random.randint(0, 6)
            if all(next_piece_type != piece.type for piece in self.engine.piece_history[-4:]): # check the last 4 pieces in the history to prevent duplicates
                break
        self.engine.next_piece.append(Piece(next_piece_type))
        self.engine.piece_history.append(Piece(next_piece_type))

    def spawn_piece(self, origin, input=None):
        if origin == 'next':
            self.engine.current_piece = self.engine.next_piece.pop(0)
            if not self.engine.hold_used:
                self.engine.level += 1 # increase level by 1 for each piece spawned
        if origin == 'hold':
            self.engine.current_piece = self.engine.hold_piece
        self.engine.current_piece.x = 2 if self.engine.big_mode else 3
        self.engine.current_piece.y = 18 if self.engine.big_mode else 19
        self.engine.update_gravity()
        if input is not None:
            if input['hold'] and not self.engine.hold_used:
                self.hold_piece(input) # if hold is pressed when spawning a piece, hold the piece instead of spawning it, and spawn the next piece in the queue. If there is no next piece in the queue, spawn the held piece instead.
            else:
                if input['ccw1'] != input['ccw2']: # if one ccw button pressed, irs by -1
                    self.rotate_current_piece(-1)
                elif input['ccw1'] and input['ccw2']:
                    self.rotate_current_piece(-2) # if both ccw buttons pressed, rotate by -2
                if input['cw1'] != input['cw2']: # if one cw button pressed, irs by 1
                    self.rotate_current_piece(1)
                elif input['cw1'] and input['cw2']:
                    self.rotate_current_piece(2) # if both cw buttons pressed, rotate by 2
        self.generate_next_piece()
        for dy in [19, 18, 17] if not self.engine.big_mode else [18, 17, 16]: # try to bump the piece up by 0, 1, or 2 cells if it spawns colliding with the stack, if it still collides after trying to bump up, the game is over
            self.engine.current_piece.y = dy
            if not self.check_piece_collision(self.engine.current_piece):
                return True
        self.engine.current_piece = None # if the piece cannot be spawned, set it to None to indicate game over
        return False

    def hold_piece(self, input):
        if self.engine.current_piece is None:
            return # if there is no active piece (e.g. it locked this frame), hold cannot be used
        if self.engine.hold_used:
            return # if hold has already been used for the current piece, do nothing
        self.engine.hold_used = True # set hold used to true to prevent holding again until the next piece spawns
        if self.engine.hold_piece is None:
            self.engine.hold_piece = self.engine.current_piece
            self.spawn_piece('next', input)
        else:
            hold_temp = self.engine.current_piece
            self.spawn_piece('hold', input)
            self.engine.hold_piece = hold_temp
        self.engine.hold_piece.orientation = 0
        self.engine.hold_piece.mask = self.engine.hold_piece.get_mask(self.engine.hold_piece.type, self.engine.hold_piece.orientation)
        

    def rotate_current_piece(self, rotation):
        kick = self.check_rotation(self.engine.current_piece, rotation=rotation)
        if kick is not None:
            self.engine.current_piece.orientation = (self.engine.current_piece.orientation + rotation) % 4
            self.engine.current_piece.mask = self.engine.current_piece.get_mask(self.engine.current_piece.type, self.engine.current_piece.orientation)
            self.engine.current_piece.x += kick[0]
            self.engine.current_piece.y += kick[1]
    
    def check_piece_collision(self, piece, dx=0, dy=0, rotation=0):
        '''
        This method checks if the given piece would collide with the board or other pieces if it were moved by (dx, dy) and rotated by rotation steps.
        It returns True if there would be a collision, and False otherwise.
        '''
        new_orientation = (piece.orientation + rotation) % 4
        new_mask = piece.get_mask(piece.type, new_orientation)
        scale = self.block_scale()
        for py in range(4):
            for px in range(4):
                if new_mask[py][px] == 1:
                    for sy in range(scale):
                        for sx in range(scale):
                            board_x = piece.x + (px * scale) + sx + dx
                            board_y = piece.y + (py * scale) + sy + dy
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
        scale = self.block_scale()
        for py in range(4):
            for px in range(4):
                if piece.mask[py][px] == 1:
                    for sy in range(scale):
                        for sx in range(scale):
                            board_x = piece.x + (px * scale) + sx
                            board_y = piece.y + (py * scale) + sy
                            if 0 <= board_y < self.engine.board.height and 0 <= board_x < self.engine.board.width:
                                self.engine.board.grid[board_y][board_x].filled = True
                                self.engine.board.grid[board_y][board_x].color = piece.color
        self.engine.current_piece = None
        self.engine.hold_used = False # reset hold usage for the next piece
        lines = self.check_line_clear() # check for line clears after locking the piece
        self.engine.lines = lines # store the lines that are being cleared in the engine to be used for drawing and collapsing after the line clear delay
        if lines:
            self.engine.state = 'line_are'
            self.clear_lines(lines)
            self.engine.line_are_counter = 0 # reset line ARE counter to start counting for the line clear delay
            self.engine.are_counter = 0
        else:
            self.engine.state = 'are'
            self.engine.are_counter = 0 # reset ARE counter to start counting for the next piece

    def check_line_clear(self):
        '''
        This method checks for line clears on the board. It should be called after locking a piece in place.
        It checks each row of the board to see if it is completely filled with minos. If a row is filled, it clears that row and moves all rows above it down by one.
        It returns the number of lines cleared.
        Sequence:
        Lock -> Line ARE -> Block fall -> ARE -> Spawn new piece
        '''
        lines_cleared = []
        for y in range(self.engine.board.height):
            if all(self.engine.board.grid[y][x].filled for x in range(self.engine.board.width)):
                lines_cleared.append(y)
        return lines_cleared

    def is_all_clear(self):
        '''
        This method checks if the board is completely clear of minos. It should be called after clearing lines to check for an all clear.
        It returns True if the board is clear, and False otherwise.
        '''
        for y in range(self.engine.board.height):
            for x in range(self.engine.board.width):
                if self.engine.board.grid[y][x].filled:
                    return False
        return True
    
    def clear_lines(self, lines):
        '''
        This method clears the given lines from the board and moves all rows above them down by one. It should be called after the line clear delay has passed.
        '''
        for y in lines:
            for x in range(self.engine.board.width):
                self.engine.board.grid[y][x].filled = False
                self.engine.board.grid[y][x].color = pygame.Color('black')
        if self.is_all_clear():
            self.engine.all_clears += 1
        lines_cleared = len(lines) // self.block_scale() # in big mode, each line clear actually clears 2 lines, so divide by the block scale to get the actual number of lines cleared for scoring and bonuses
        self.engine.lines_cleared += lines_cleared
        self.engine.time += self.engine.get_time_bonus(lines_cleared=lines_cleared, all_clear=self.is_all_clear()) # add time bonus for clearing lines, more for more lines and all clear
        self.engine.level += self.engine.get_level_bonus(lines_cleared=lines_cleared) # add level bonus for clearing lines

    def collapse_lines(self, lines):
        '''
        This method collapses the given lines from the board by moving all rows above them down by one. It should be called after the line clear delay has passed and the lines have been cleared.
        '''
        for y in sorted(lines):
            for row in range(y, 0, -1):
                for x in range(self.engine.board.width):
                    self.engine.board.grid[row][x].filled = self.engine.board.grid[row - 1][x].filled
                    self.engine.board.grid[row][x].color = self.engine.board.grid[row - 1][x].color
            for x in range(self.engine.board.width):
                self.engine.board.grid[0][x].filled = False
                self.engine.board.grid[0][x].color = pygame.Color('black')


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
        kick_step = self.kick_step()
        if piece.type == 6: # O-piece, no kicks
            return None
        elif piece.type in [1, 2, 3, 4, 5]: # T, L, J, S, Z
            for dx in [kick_step, -kick_step]: # Try kicks to the right and left
                if not self.check_piece_collision(piece, dx=dx, dy=0, rotation=rotation):
                    if piece.type in [1, 2, 3] and piece.orientation % 2 == 0 and self.check_center_column(piece, rotation): # from 3-wide to 2-wide, no kick off center column
                            continue
                    return (dx, 0) # Kick by dx cells horizontally
            t_floor_kick = -kick_step
            if piece.type == 1 and (piece.orientation + rotation) % 4 == 2 and piece.floorkicks == 0 and self.check_piece_collision(piece, dx=0, dy=1) and not self.check_piece_collision(piece, dx=0, dy=t_floor_kick, rotation=rotation): # T-piece, rotating flat side down, try floor kick if the piece is touching the stack and hasn't floorkicked yet
                piece.floorkicks += 1
                return (0, t_floor_kick) # Floor kick upwards
            return None # Rotation not possible
        else: # I-piece
            if (piece.orientation + rotation) % 2 == 0 and (self.check_piece_collision(piece, dx=-kick_step, dy=0) or self.check_piece_collision(piece, dx=kick_step, dy=0)): # from 1 wide to 4-wide, needs to be touching stack to kick
                for dx in [kick_step, 2 * kick_step, -kick_step]:
                    if not self.check_piece_collision(piece, dx=dx, dy=0, rotation=rotation):
                        return (dx, 0) # Horizontal kick by dx cells
            elif (piece.orientation + rotation) % 2 == 1 and self.check_piece_collision(piece, dx=0, dy=1) and piece.floorkicks == 0: # needs to be touching stack to floor kick
                for dy in[-kick_step, -2 * kick_step]:
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
        hold = keys[pygame.K_LSHIFT]

        return {
            'left': left,
            'right': right,
            'ccw1': ccw1,
            'cw1': cw1,
            'ccw2': ccw2,
            'cw2': cw2,
            'soft_drop': soft_drop,
            'hard_drop': hard_drop,
            'hold': hold
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
            move_step = self.horizontal_step()
            if input is not None:
                if input['ccw1'] and not self.held_input['ccw1']:
                    self.rotate_current_piece(rotation=-1)
                elif input['cw1'] and not self.held_input['cw1']:
                    self.rotate_current_piece(rotation=1)

                if input['ccw2'] and not self.held_input['ccw2']:
                    self.rotate_current_piece(rotation=-1)
                elif input['cw2'] and not self.held_input['cw2']:
                    self.rotate_current_piece(rotation=1)

                if input['right'] != input['left']: # if both left and right are pressed, or neither are pressed, don't move the piece horizontally
                    if input['right']:
                        if not self.held_input['right'] or (self.held_input['right'] == self.held_input['left']):
                            if not self.check_piece_collision(self.engine.current_piece, dx=move_step):
                                self.engine.current_piece.x += move_step
                        else:
                            self.engine.das_counter += 1
                            if self.engine.das_counter >= self.engine.das:
                                self.engine.arr_counter += 1
                                if self.engine.arr_counter >= self.engine.arr:
                                    if not self.check_piece_collision(self.engine.current_piece, dx=move_step):
                                        self.engine.current_piece.x += move_step
                                    self.engine.arr_counter = 0 
                    elif input['left']:
                        if not self.held_input['left'] or (self.held_input['left'] == self.held_input['right']):
                            if not self.check_piece_collision(self.engine.current_piece, dx=-move_step):
                                self.engine.current_piece.x -= move_step
                        else:
                            self.engine.das_counter += 1
                            if self.engine.das_counter >= self.engine.das:
                                self.engine.arr_counter += 1
                                if self.engine.arr_counter >= self.engine.arr:
                                    if not self.check_piece_collision(self.engine.current_piece, dx=-move_step):
                                        self.engine.current_piece.x -= move_step
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

                if input['hold'] and not self.held_input['hold'] and self.engine.current_piece is not None:
                    self.hold_piece(input)
        else:
            if self.engine.state == 'are':
                if input['right'] != input['left']:
                    if input['right']:
                        if self.held_input['right'] and (self.held_input['right'] != self.held_input['left']):
                            self.engine.das_counter += 1
                    elif input['left']:
                        if self.held_input['left'] and (self.held_input['left'] != self.held_input['right']):
                            self.engine.das_counter += 1
                else:
                    self.engine.das_counter = 0
                    self.engine.arr_counter = 0
                self.engine.are_counter += 1
                self.engine.gravity_counter = 0
                if self.engine.are_counter >= self.engine.are:
                    self.engine.are_counter = 0
                    self.spawn_piece('next', input)
                    self.engine.state = 'active'
            elif self.engine.state == 'line_are':
                self.engine.line_are_counter += 1
                self.engine.gravity_counter = 0
                if self.engine.line_are_counter >= self.engine.line_are:
                    self.collapse_lines(self.engine.lines) # collapse the cleared lines before spawning the next piece
                    self.engine.line_are_counter = 0
                    self.engine.state = 'are'

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
        self.game = None
        self.hud_font = pygame.font.SysFont("Lucida Console", 32)
    
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
        scale = 2 if self.engine.big_mode else 1
        for py in range(4):
            for px in range(4):
                if piece.mask[py][px] == 1:
                    for sy in range(scale):
                        for sx in range(scale):
                            if piece.x + (px * scale) + sx == x and piece.y + (py * scale) + sy == y:
                                return True
        return False
    
    def draw_next_pieces(self):
        for i in range(6):
            piece = self.engine.next_piece[i]
            if piece is not None:
                for py in range(4):
                    for px in range(4):
                        if piece.mask[py][px] == 1:
                            pygame.draw.rect(self.screen, piece.color, (HORIZONATAL_OFFSET + (3 + 4 * i) * 16 + px * 16, 2 * 16 + py * 16, 16, 16))
        
    def draw_hold_piece(self):
        piece = self.engine.hold_piece
        if piece is not None:
            for py in range(4):
                for px in range(4):
                    if piece.mask[py][px] == 1:
                        pygame.draw.rect(self.screen, piece.color, (HORIZONATAL_OFFSET + px * 16 - 4 * 16, 4 * 16 + py * 16, 16, 16))

    def format_time(self, time):
        minutes = time // 3600
        seconds = (time % 3600) // 60
        centiseconds = round(time % 60 / FPS * 100)
        return f"{minutes:02d}:{seconds:02d}:{centiseconds:02d}"

    def draw_right_info(self):
        board_right = HORIZONATAL_OFFSET + 10 * 16
        visible_top = VERTICAL_OFFSET + 30 * 16
        x = board_right + 24
        y = visible_top
        line_gap = 34

        info_lines = [
            f"Time: {self.format_time(max(0, self.engine.time))}",
            f"All Clears: {self.engine.all_clears}",
            f"Level: {self.engine.level}",
        ]

        for idx, text in enumerate(info_lines):
            text_surface = self.hud_font.render(text, True, pygame.Color('black'))
            self.screen.blit(text_surface, (x, y + idx * line_gap))

    def debug_display_input(self):
        input = self.game.held_input
        input_text = f"Input: {'L' if input['left'] else ''}{'R' if input['right'] else ''}{'CCW1' if input['ccw1'] else ''}{'CW1' if input['cw1'] else ''}{'CCW2' if input['ccw2'] else ''}{'CW2' if input['cw2'] else ''}{'SD' if input['soft_drop'] else ''}{'HD' if input['hard_drop'] else ''}{'HOLD' if input['hold'] else ''}"
        text_surface = self.hud_font.render(input_text, True, pygame.Color('black'))
        self.screen.blit(text_surface, (HORIZONATAL_OFFSET, VERTICAL_OFFSET + 30 * 16 + 6 * 34))
    
    

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 640, 480
HORIZONATAL_OFFSET = (WIDTH - 10 * 16) // 4
VERTICAL_OFFSET = -(20 * 16) + (HEIGHT - 20 * 16) // 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto-Konoha")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

game = Game()
renderer = Renderer(screen)
renderer.engine = game.engine
renderer.game = game
game.spawn_piece('next')

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
    renderer.draw_next_pieces()
    renderer.draw_hold_piece()
    renderer.draw_right_info()
    renderer.debug_display_input()
    
    # Update display
    pygame.display.flip()

pygame.quit()