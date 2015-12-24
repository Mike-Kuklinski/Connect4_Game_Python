# -*- coding: utf-8 -*-
"""
Connect Four PyGame Code
Created on Sat Jul 18 14:10:55 2015

@author: Mike Kuklinski
"""

# Import necessary modules
import pygame
import sys
import copy
import math
import random
import time


# Program Structure

###############################################################################
# 1. Globals and Dictionaries

# Global Variables
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
CHIP_DIAMETER = 40
NUM_CHIP_WIDE = 7
NUM_CHIP_HIGH = 6
CHIP_SPACING = 10
WIN_LENGTH = 4
CHIP_AREA = ((0,(DISPLAY_HEIGHT*0.9)),((DISPLAY_WIDTH/10),(DISPLAY_HEIGHT/10)))
PLAYER_1 = 'RED'
PLAYER_2 = 'BLUE'
FIRST_TURN = PLAYER_1

"""
Cutoff settings for deciding which move to make by the computer based on
the percent of empty spaces remaining.

Init. - Monte Carlo with NTRIAL[0] iterations
MOVE_STRATEGY[0] - Monte Carlo with NTRIAL[1] iterations
MOVE_STRATEGY[1] - DFS without Trimming
"""
MOVE_STRATEGY = [0.80, 0.70] # Percent of emtpy spaces remaining 
NTRIALS = [500,1000]
MOVE_TIME = 10
#==============================================================================
# Grid str representation dictionary
CHIP_LETTER = {'WHITE' : 'E',
              'RED' : 'R',
              'BLUE' : 'B'}

# Score dictionary
SCORES = {'RED' : 1, 
          'BLUE' : -1,
          'DRAW' : 0,
          'NONE' : None}

# Direction Dictionary for checking in-a-row values          
DIR = {'UR' : [1, -1],
       'R' : [1, 0],
       'DR' : [1, 1],
       'D' : [0, 1]}

# Best Move Dictionary 
BEST = {'RED' : {'best' : (-5, [-1, -1], 1000), 'win' : 1, 'lose' : -1},
        'BLUE' : {'best' : (5, [-1, -1], 1000), 'win' : -1, 'lose' : 1}}

BRAIN = {'RED' : 'Human',
         'BLUE' : 'Computer'}
         

# Grid state tracking dictionaries for computer moves
P1_grid_states = {}     
P2_grid_states = {}

###############################################################################          
# 2. Helper Functions

def grid_reset():
    """
    Reset grid state dictionaries for tracking optimal moves based on grid states
    """
    global P1_grid_states, P2_grid_states
    P1_grid_states = {}
    P2_grid_states = {}

def set_first_turn(player):
    """
    Function to change who goes first
    """
    global FIRST_TURN
    FIRST_TURN = player
    
def set_opponent(opponent):
    """
    Function to change who player is against
    """
    global BRAIN
    BRAIN[PLAYER_2] = opponent
    
def idx_to_pos(idx):
    """
    Helper function which takes a pair of grid indices and return the position
    indices of that index.
    """
    x_pos = (board._loc[0] + ((CHIP_DIAMETER + CHIP_SPACING)/2) + 
    (CHIP_DIAMETER + CHIP_SPACING)*idx[0])
    y_pos = (board._loc[1] + ((CHIP_DIAMETER + CHIP_SPACING)/2) + 
    (CHIP_DIAMETER + CHIP_SPACING)*idx[1])
    return (x_pos, y_pos)

def mirror_move(move, board_width):
    """
    Takes a move (score, [col, row], trace), and returns the mirror opposite
    of the move (score, [opp_col, row], trace) to make on the board
    """
    move_idx = move[1]
    idx_1 = (board_width - 1) - move_idx[0]
    idx_2 = move_idx[1]
    mirror_idx = [idx_1, idx_2]
    mirror_move = list(move)
    mirror_move[1] = mirror_idx
    return mirror_move

def check_move():
    """
    Function which determines if a human or computer is playing and makes a move
    if necessary
    """
    current_brain = BRAIN[current_gstate._player_turn]
    if (current_brain == 'Computer' and current_gstate._AI_in_progress == False
    and current_gstate._game_over == False):
        pos = (DISPLAY_WIDTH-30, DISPLAY_HEIGHT-30)
        #start = time.time()
        move = get_move(board, current_gstate)
        #stop = time.time() - start
        #print 'time elapsed ' , stop
        new_chip = Chip(current_gstate._player_turn, pos, True, Move = move[1])
        current_gstate.pick_chip(new_chip)
        current_gstate.set_AI_status(True)

##############################################################################
# Computer Functions    
    
def get_move(game_board, game_state, trace = 1):
    """
    Function which evaluates the current full board and determines which
    sub-move function to call (Monte Carlo or Depth First Search). If time remains
    for move, then computer will begin building a move dictionary
    """
    empty_spaces = len(game_board.get_state_indices('WHITE'))
    total_spaces = NUM_CHIP_HIGH*NUM_CHIP_WIDE
    init_time = time.time()
    if empty_spaces >= math.ceil(MOVE_STRATEGY[0] * total_spaces):
        #print 'Monte Carlo Move Selected (',NTRIALS[0],'trials)'
        selected_move = board_move_MC(game_board, game_state, NTRIALS[0])
    elif empty_spaces >= math.ceil(MOVE_STRATEGY[1] * total_spaces):
        #print 'Monte Carlo Move Selected (',NTRIALS[1],'trials)'
        selected_move = board_move_MC(game_board, game_state, NTRIALS[1])
#    elif empty_spaces >= math.ceil(MOVE_STRATEGY[2] * total_spaces):
#        if game_state._player_turn == PLAYER_1:
#            print 'Trimmed Depth First Search Move Selected'
#            selected_move = board_move_DFS(game_board, game_state, P1_trim_grid_state, True, trace)
#        else:
#            print 'Trimmed Depth First Search Move Selected'
#            selected_move = board_move_DFS(game_board, game_state, P2_trim_grid_state, True, trace)
    else:
        if game_state._player_turn == PLAYER_1:
            #print 'Full Depth First Search Move Selected'
            selected_move = board_move_DFS(game_board, game_state, P1_grid_states, False, trace, 15)
        else:
            #print 'Full Depth First Search Move Selected'
            selected_move = board_move_DFS(game_board, game_state, P2_grid_states, False, trace, 15)
    if selected_move == None:
        #print 'time expired, reverting to monte carlo'
        selected_move = board_move_MC(game_board, game_state, NTRIALS[1])
    time_remaining = MOVE_TIME - (time.time() - init_time)
    #print 'move time is', time_remaining
    if time_remaining > 0:
        if game_state._player_turn == PLAYER_1:
            #print 'Building player 1 dictionary'
            board_move_DFS(game_board, game_state, P1_grid_states, True, trace, time_remaining)        
        else:
            #print 'Building player 2 dictionary'
            board_move_DFS(game_board, game_state, P2_grid_states, True, trace, time_remaining)
    return selected_move

#==============================================================================
# Monte Carlo (MC) Approach

def board_move_MC(game_board, game_state, ntrials):
    """
    Perform a Monte Carlo on the current board and return the available move
    with the best score.
    """
    # Initialize score tracking and player turns
    score_track = {}
    for col in range(NUM_CHIP_WIDE):
        for row in range(NUM_CHIP_HIGH):
            score_track[(col,row)] = 0
    current_player = game_state._player_turn
    opponent = game_state.get_opponent()
    # Iterate through the number of trials tracking the score for each space
    for iteration in range(ntrials):
        cloned_board = game_board.clone()
        cloned_state = game_state.clone()
        MC_playout(cloned_board, cloned_state, score_track)
        result = cloned_board.check_win(cloned_state)
        if result != 'DRAW':
            MC_update_score(score_track, cloned_board, result, current_player, opponent)
    # With all the grid spaces score, select the available move with highest score
    max_score = -float('inf')
    for move in game_board.get_available_moves():
        if score_track[tuple(move)] > max_score:
            max_score = score_track[tuple(move)]
            best_move = move
    return (max_score, best_move)

def MC_playout(game_board, game_state, scores):
    """
    Function which plays out a game board with proportional-random moves 
    until the game is over.
    """
    while game_state._winner == None:
        temp_player = game_state._player_turn
        avail_moves = game_board.get_available_moves()
        # Adjust probabilities of 'random' move selection based on score performance
        for move in avail_moves[:]:
            if scores[tuple(move)] > 0:
                for count in range(scores[tuple(move)]):
                    avail_moves.append(move)
        selected_move = random.choice(avail_moves)
        game_board.quick_add(selected_move, temp_player)
        game_board.check_win(game_state)
        game_state.switch_turn()
        
def MC_update_score(scores, game_board, winner, current_player, opponent):
    """
    Scores a finished game board and updates score tracking accordingly for 
    each space
    """
    moves = scores.keys()
    for move in moves:
        if current_player == winner:
            if game_board._grid[move[0]][move[1]] == current_player:
                scores[move] += 1
            elif game_board._grid[move[0]][move[1]] == opponent:
                scores[move] -= 1
        else:
            if game_board._grid[move[0]][move[1]] == current_player:
                scores[move] -= 1
            elif game_board._grid[move[0]][move[1]] == opponent:
                scores[move] += 1

#=============================================================================
# Depth First Search (DFS) Move Approach

def board_move_DFS(game_board, game_state, grid, trim, trace, time_check = float('inf')):
    """
    Determine optimal move to make on a given board and game state
    using a recurvise Depth First tree Search with optional trimming of branches.
    
    Returns a tuple with three elements. (Score, [column, row], Trace Length)
    """
    # Set initial variables based on full versus subset set board search
    temp_player = game_state._player_turn    
    current_grid = str(game_board._grid)
    start_time = time.time()
    
    # Check if move for current grid has already been determined and if so, use it
    if current_grid in grid:
        best_move = grid[current_grid]
        return best_move
    elif (time.time()-start_time) < time_check:# If current grid was has not already been determined, run recursion on it.
        move_list = []
        # Determine the score of each potential move for each board arrrangement
        avail_moves = game_board.get_available_moves()
        random.shuffle(avail_moves)
        #for potential_move in game_board.get_available_moves():
        for potential_move in avail_moves:
            if (time.time()-start_time) < time_check:
                cloned_board = game_board.clone()
                cloned_game_state = game_state.clone()
                cloned_board.quick_add(potential_move, temp_player)
                result = cloned_board.check_win(cloned_game_state, WIN_LENGTH)           
                cloned_game_state.switch_turn()
                # If a terminate state is found for a move, log the move info accordingly 
                if result != None:
                    move_list.append((SCORES[result], potential_move, trace))
                    # If trimming, break loop at a guarenteed win or loss.
                    if trim:
                        if temp_player == PLAYER_1:
                            if result == PLAYER_1:
                                break
                        elif temp_player == PLAYER_2:
                            if result == PLAYER_2:
                                break
                # If terminate state is not found, continued recursion on opponents move            
                else:
                    new_time = time_check - (time.time() - start_time)
                    opp_move = board_move_DFS(cloned_board, cloned_game_state, grid, trim, (trace + 1), new_time)
                    if opp_move != None:
                        move_list.append((opp_move[0], potential_move, opp_move[2]))
                        # If trimming, break loop at a guarenteed win or loss.
                        if trim:
                            if temp_player == PLAYER_1:
                                if opp_move[0] == 1:
                                    break
                            elif temp_player == PLAYER_2:
                                if opp_move[0] == -1:
                                    break
        # Once all moves and scores are logged, determine, optimal move
        if (time.time()-start_time) < time_check:
            best_move = get_best_score(move_list, temp_player)                    
            # Store a mirrored board and move in the move dictionary
            mirrored_best_move = mirror_move(best_move, NUM_CHIP_WIDE)
            mirrored_grid = game_board.get_mirror_grid()
            grid[current_grid] = best_move
            grid[str(mirrored_grid)] = mirrored_best_move
            return best_move

def get_best_score(mlist, player):
    """
    Helper function to search through potential moves and return best move
    while taking into account, the number of move ahead.
    """
    if len(mlist) == 0:
        return None
    min_trace = float('inf')
    max_trace = 0
    # Index moves based on their score value
    score_trace = {-1:[], 0:[], 1:[]}
    for move in mlist:
        score_trace[move[0]].append(move)
    # Determine the best score based on which player turn it is
    best_score = BEST[player]['best']
    if best_score[0] < 0:
        for move in mlist:
            if move[0] > best_score[0]:
                best_score = move
    else:
        for move in mlist:
            if move[0] < best_score[0]:
                best_score = move
    # If best move is a winning scenario, select quickest route
    if best_score[0] == BEST[player]['win']:
        for move in score_trace[best_score[0]]:
            if move[2] < min_trace:
                min_trace = move[2]
                best_score = move
    # If best move is a losing scenario, select longest route            
    elif best_score[0] == BEST[player]['lose']:
        for move in score_trace[best_score[0]]:
            if move[2] > max_trace:
                max_trace = move[2]
                best_score = move    
    return best_score


###############################################################################
# 3. Classes
        
class GameState():
    """
    Class Object for tracking the state of the game
    """
    def __init__(self):
        """
        Initialize Variables for starting point of a game.
        """
        self._player_turn = FIRST_TURN
        self._chip_in_play = []
        self._game_over = True
        self._winner = None
        self._AI_in_progress = False
                     
    def __str__(self):
        """
        Print a string representation of the game state
        """
        ans = ''
        ans += '\n Game Over: ', str(self._game_over)
        ans += '\n Winner is: ', str(self._winner)
        ans += '\n Current Turn: ', str(self._player_turn)
        return ans
        
    def start_game(self):
        self.__init__()
        self._game_over = False
       
    def set_AI_status(self, boolean):
        self._AI_in_progress = boolean
        
    def pick_chip(self, chip):
        self._chip_in_play.append(chip)

    def clear_chip(self): # Keep
        self._chip_in_play = []
    
    def get_chip(self): # keep
        if len(self._chip_in_play) > 0:
            return self._chip_in_play[0]
        else: return []
    
    def clone(self):
        return copy.deepcopy(self)
    
    def switch_turn(self):
        if not self._game_over:
            if self._player_turn == PLAYER_1:
                self._player_turn = PLAYER_2
            elif self._player_turn == PLAYER_2:
                self._player_turn = PLAYER_1
    
    def get_opponent(self):
        if self._player_turn == PLAYER_1:
            return PLAYER_2
        elif self._player_turn == PLAYER_2:
            return PLAYER_1
   
    def declare_win(self, draw = False):
        if draw == False:
            self._winner = self._player_turn
        else: 
            self._winner = 'DRAW'    
        self._game_over = True

#==============================================================================        
class Chip:
    """
    Chip Object with associated player and location
    """
    def __init__(self, player, location, AI = False, Move = None):
        """
        Initialize variables associated with Chip Class Object
        """
        self._player = player       
        self._color = pygame.Color(player)
        self._loc = list(location)
        self._state = 'In Hand'
        self._AI = AI
        self._move = Move
        self._add_to_board = False
    
    def draw(self, canvas):
        """
        Draw chip on screen
        """
        pygame.draw.circle(canvas, self._color, self._loc, (CHIP_DIAMETER/2))
    
    def change_state(self, new_state):
        """
        Function to switch the state of the chip to adjust how it moves, 'In Hand',
        'Legal Drop', 'Illegal Drop'
        """
        self._state = new_state
        
    def get_column_idx(self, game_board):
        """
        Function which returns which column index a chip is currently located.
        """
        column_idx = int((math.ceil((float(self._loc[0]) - game_board._loc[0]) / 
                    (CHIP_DIAMETER + CHIP_SPACING))) - 1)
        return column_idx
                    
    def update_loc(self):
        """
        Updates the position of the chip on the board based on the mouse
        location.
        """
        # When a chip is being held, it should follow the location of the mouse
        if not self._AI:
            if self._state == 'In Hand':
                self._loc = pygame.mouse.get_pos()
             
            # If a legal drop is made, the chip should fall into a slot on the board    
            elif self._state == 'Legal Drop':
                if self._add_to_board:
                    board.add_chip(self, current_gstate)
                else:
                    column_idx = self.get_column_idx(board)
                    empty_slot = board.get_empty_slot(column_idx)
                    final_pos = idx_to_pos((column_idx, empty_slot))
                    self._loc = list(self._loc)
                    self._loc[0] = final_pos[0]
                    if self._loc[1] < final_pos[1] - 15:
                        self._loc[1] += 15
                    if self._loc[1] >= final_pos[1] - 15:
                        self._loc[1] = final_pos[1]
                        self._add_to_board = True
            # If the chip was illegally dropped, this code makes it fall to
            # the ground and return to the chip pile.
            else:
                self._loc = list(self._loc)
                if self._loc[1] + (CHIP_DIAMETER/2) < DISPLAY_HEIGHT:
                    self._loc[1] += 15
                elif self._loc[0] - (CHIP_DIAMETER/2) > 0:
                    self._loc[0] -= 15
                else:
                    current_gstate.clear_chip()
        else: 
            # If the chip is an computer chip, then follow the drop path based on the 
            # computer's move
            self._loc = list(self._loc)
            final_pos = idx_to_pos(self._move)
            if self._loc[1] > 50 and self._loc[0] == DISPLAY_WIDTH - 30:
                self._loc[1] -= 5
            elif self._loc[0] > final_pos[0]:
                self._loc[0] -= 5
            elif self._loc[1] < final_pos[1]:
                self._loc[1] += 15
            else:
                board.add_chip(self, current_gstate)
                current_gstate.set_AI_status(False)

#==============================================================================
class GameBoard:
    """
    GameBoard class which keeps track of all the chip locations and draws
    the board accordingly.
    """
    def __init__(self, x_chips, y_chips, win_length, grid = None):
        """
        Initialize variables associated with GameBoard Class Object
        """
        self._x_chips = x_chips
        self._y_chips = y_chips
        self._win_length = win_length
        self._color = pygame.Color('Yellow')
        self._width = (CHIP_DIAMETER + CHIP_SPACING) * self._x_chips
        self._height = (CHIP_DIAMETER + CHIP_SPACING) * self._y_chips
        self._loc = ((DISPLAY_WIDTH-self._width)/2,(DISPLAY_HEIGHT-self._height)/2) 
        self._rect = (self._loc, (self._width, self._height))
        if grid == None:
            self._grid = {}
            self.init_grid()
        else:
            self._grid = grid
        
    def __str__(self):
        """
        Print a text representation of the current grid
        """
        grid = ''
        for row_idx in range(self._y_chips):
            grid += '|'            
            for col_idx in range(self._x_chips):
                grid += CHIP_LETTER[self._grid[col_idx][row_idx]] 
                grid += '|'
            grid += '\n'
            for col_idx in range(self._x_chips):
                grid += '--'
            grid += '\n'
        return grid
    
    def init_grid(self):
        """
        Creates a list representation of the board grid based on initial sizes.
        Board grid to be called by grid[column][row].
        """
        self._grid = [['WHITE' for row_idx in range(self._y_chips)] for col_idx in range(self._x_chips)] 
    
    def get_mirror_grid(self):
        """
        Function which takes the grid representation and mirrors the column
        ordering
        """
        mirror_grid = copy.deepcopy(self._grid)
        mirror_grid.reverse()
        return mirror_grid
    
    def get_available_moves(self):
        """
        Scans the board grid and returns a list of indices containing available
        moves.
        """
        avail_moves = []
        for col_idx in range(self._x_chips):
            potential_move = self.get_empty_slot(col_idx) 
            if  potential_move != None:
                avail_moves.append([col_idx, potential_move])
        return avail_moves

    def add_chip(self, chip, game_state, switch = True):
        """
        Updates the grid, adding a chip to the board at the column location 
        it was dropped, at the lowest possible slot.
        """
        chip_column = chip.get_column_idx(self)
        empty_slot = self.get_empty_slot(chip_column)
        
        if empty_slot != None:
            game_state.clear_chip()
            self._grid[chip_column][empty_slot] = game_state._player_turn
            self.check_win(game_state)
            if game_state._game_over == False and switch == True:
                game_state.switch_turn()
        
    def quick_add(self, idx, player):
        """
        Changes state of particular grid slot to a given player
        """
        self._grid[idx[0]][idx[1]] = player
    
    def get_empty_slot(self, column):
        """
        Returns the lowest empty row a chip can be placed in a given column
        """
        if column >= NUM_CHIP_WIDE:
            pass
            #print 'column out of bounds at', column
        elif self._grid[column][0] == 'WHITE':
            for row_idx in range(self._y_chips):
                if self._grid[column][row_idx] != 'WHITE':
                    empty_row = row_idx - 1 
                    break
                elif row_idx == self._y_chips - 1:
                    empty_row = row_idx
                    break
            return empty_row
        else: 
            return None
    
    def check_adjacent_state(self, current_cell, direction):
        """
        Returns the state of the cell adjacent to  the current cell in 
        a particular direction ('UR', 'R', 'DR', 'D'). The input is the index 
        of the cell (column_num, row_idx).
        """
        # Determine state of current cell
        current_cell_state = self._grid[current_cell[0]][current_cell[1]]
        # Determine location of adjacent cell based on direction
        new_col = current_cell[0] + DIR[direction][0]
        new_row = current_cell[1] + DIR[direction][1]
        # Check if cell exists and if so, check state of adjacent cell
        if 0 <= new_col <= self._x_chips-1 and 0 <= new_row <= self._y_chips - 1:
            adjacent_cell_state = self._grid[new_col][new_row]
            if current_cell_state == adjacent_cell_state: return True
            else: return False
        else: return False
        
    def check_win(self, game_state, in_a_row = WIN_LENGTH):
        """
        Scans the board grid and checks for tiles of the same color within
        the same row (vertical, horizontal, diaganol) of a given distance. Returns
        the outcome of the game (player Red or Blue, Draw, None).
        """
        player = game_state._player_turn
        win_indices = self.get_state_indices(player)
        avail_moves = self.get_available_moves()
        for cell in win_indices:
            for directions in DIR:
                temp_cell = cell[:]
                win_check = 1
                for iterations in range(in_a_row):
                    if self.check_adjacent_state(temp_cell, directions) == True:
                        win_check += 1
                        temp_cell[0] += DIR[directions][0]
                        temp_cell[1] += DIR[directions][1]
                if win_check == in_a_row:
                    game_state.declare_win()
                    break
            if game_state._game_over: break

       # Check for Draw
        if len(avail_moves) == 0 and game_state._winner == None:
            game_state.declare_win(draw = True)
        return game_state._winner

    def get_state_indices(self, state):
        """
        Returns list of indices in grid which contains the specified state.
        """
        index_list = []
        for col_idx in range(self._x_chips):
            for row_idx in range(self._y_chips):
                if self._grid[col_idx][row_idx] == state:
                    index_list.append([col_idx, row_idx])
        return index_list
     
    def clone(self):
        """
        Creates a copy of the current board fo recurtion purposes
        """
        clone_board = copy.deepcopy(self)
        return clone_board
    
    def draw(self, canvas):
        """
        Draws the main board and iterates over the spaces to draw them as either
        empty, Red, or Blue.
        """
        rect = pygame.Rect(self._rect)
        pygame.draw.rect(canvas, self._color, rect)
        for col_idx in range(self._x_chips):
            for row_idx in range(self._y_chips):
                chip_loc = idx_to_pos((col_idx, row_idx))
                chip_state = self._grid[col_idx][row_idx]
                chip_color = pygame.Color(chip_state)
                pygame.draw.circle(canvas, chip_color, chip_loc, CHIP_DIAMETER/2)
    
###############################################################################   
# 4. Define Event Handler Functions

def mdown_handler(pos):
    """
    Handler for when mouse button is down, to select options and move chips
    """
    global red_stack, blue_stack, new_game_button
    # New Game Button Interaction
    if current_gstate._game_over == True:
        if start_button.collidepoint(pos):
            grid_reset()
            current_gstate.start_game()
            board.init_grid()
    else:
        if stop_button.collidepoint(pos):
            grid_reset()
            current_gstate._game_over = True
            board.init_grid()        
    # First turn selection   
    if current_gstate._game_over == True:
        if First_button.collidepoint(pos):
            set_first_turn(PLAYER_1)
        elif Second_button.collidepoint(pos):
            set_first_turn(PLAYER_2)
    # Opponent selection
    if current_gstate._game_over == True:
        if vs_hum_button.collidepoint(pos):
            set_opponent('Human')
        elif vs_nick_button.collidepoint(pos):
            set_opponent('Computer')
    # Chip Stack Interaction    
    if current_gstate._game_over == False:
        # Pick up chip for respective player
        if current_gstate._player_turn == PLAYER_1:
            if red_stack.collidepoint(pos):
                new_chip = Chip(PLAYER_1, pos)
                current_gstate.pick_chip(new_chip)
                new_chip.change_state('In Hand')
        elif current_gstate._player_turn == PLAYER_2:
            if blue_stack.collidepoint(pos):
                new_chip = Chip(PLAYER_2, pos)
                current_gstate.pick_chip(new_chip)
                new_chip.change_state('In Hand')
                
def mup_handler(pos):
    """
    Handler for when mouse button is released, to drop chips.
    """
    if (current_gstate.get_chip() != [] and 
    current_gstate._game_over == False):
        chip = current_gstate.get_chip()
        if chip._state == 'In Hand':
            # Check if chip was released in a legal area above the board and if
            # so, add the chip to the board.
            if ((pos[1] + (CHIP_DIAMETER/2) < (DISPLAY_HEIGHT - board._height)/2) and
                ((DISPLAY_WIDTH - board._width) / 2) < pos[0] <
                ((DISPLAY_WIDTH - board._width) / 2) + board._width and
                board.get_empty_slot(chip.get_column_idx(board)) != None):
                    chip.change_state('Legal Drop')
            else: 
                chip.change_state('Illegal Drop')
                
        
def draw_handler(canvas):
    """
    Overall drawing handler which draws each element and calls for updates
    in positions.
    """
    global red_stack, blue_stack, First_button, Second_button, start_button, stop_button
    global vs_hum_button, vs_nick_button
    #==================Initialize==============================================
    # Initialize Fonts
    comic_sans_10 = pygame.font.Font(pygame.font.match_font('comicsansms'), 10)
    comic_sans_18 = pygame.font.Font(pygame.font.match_font('comicsansms'), 18)
    comic_sans_25 = pygame.font.Font(pygame.font.match_font('comicsansms'), 25)
    # Clear canvas for beginning of frame
    canvas.fill(pygame.Color('white'))
    # Draw Board add associated elements
    board.draw(canvas)
    # Draw chips in play
    chip = current_gstate.get_chip()
    if chip != []:
        chip.update_loc() 
        chip.draw(canvas)    
    #    
    #===================Interactive Buttons====================================
    # Draw Chip Stacks
    #    Red    
    pygame.draw.rect(canvas,  pygame.Color('Red'), red_chip_outline)
    red_stack = canvas.blit(red_chip_stack, (0,DISPLAY_HEIGHT-70))
    #    Blue
    pygame.draw.rect(canvas,  pygame.Color('Blue'), blue_chip_outline)
    blue_stack = canvas.blit(blue_chip_stack, (DISPLAY_WIDTH - 125,DISPLAY_HEIGHT-70))
    # Draw Start/Stop Buttons
    start_button = canvas.blit(start_b, (DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT - 70))
    stop_button = canvas.blit(stop_b, (DISPLAY_WIDTH/2 - 0, DISPLAY_HEIGHT - 70))
    # Draw First Turn Selector
    if current_gstate._game_over == True:
        move_selection = comic_sans_18.render('Would you like to go:', True, pygame.Color('Black'))
        canvas.blit(move_selection, (3, 55))
        First = comic_sans_18.render('First', True, pygame.Color('Dark Green'))
        First_button = canvas.blit(First, (3, 80))
        Second = comic_sans_18.render('Second', True, pygame.Color('Dark Green'))
        Second_button = canvas.blit(Second, (3, 105))
        if FIRST_TURN == PLAYER_1:
            pygame.draw.circle(canvas, pygame.Color('Brown'), (100, 95), 8)
        else:
            pygame.draw.circle(canvas, pygame.Color('Brown'), (100, 120), 8)
    # Draw computer versus human Selector
    if current_gstate._game_over == True:
        ai_selection = comic_sans_18.render('Who would you like to play?:', True, pygame.Color('Black'))
        canvas.blit(ai_selection, (DISPLAY_WIDTH-225, 55))
        vs_hum = comic_sans_18.render('A Friend', True, pygame.Color('Dark Green'))
        vs_hum_button = canvas.blit(vs_hum, (DISPLAY_WIDTH-125, 80))
        vs_nick = comic_sans_18.render("Nicolas", True, pygame.Color('Dark Green'))
        vs_nick_button = canvas.blit(vs_nick, (DISPLAY_WIDTH-125, 105))
        if BRAIN[PLAYER_2] == 'Computer':
            pygame.draw.circle(canvas, pygame.Color('Brown'), (DISPLAY_WIDTH-20, 120), 8)
        else:
            pygame.draw.circle(canvas, pygame.Color('Brown'), (DISPLAY_WIDTH-20, 95), 8)
    #================Game State Messages=======================================
    #   Indicate whose turn it is    
    if current_gstate._game_over:
        plyr_message = "Press 'Start' to begin, and 'Stop' during play to reset"
    else:
        plyr_message = "Player %s's Turn." % (current_gstate._player_turn)
    player_notice = comic_sans_18.render(plyr_message, True, pygame.Color('Black'))
    canvas.blit(player_notice, (3, 5))
    #   Indicate if game has been won
    if current_gstate._game_over == True and current_gstate._winner != None:
        if current_gstate._winner == 'DRAW':
            game_message = "DRAW!"
        elif current_gstate._winner != None:
            game_message = "Player %s WINS!" % (current_gstate._winner)
    else:
        game_message = ""
    game_notice = comic_sans_25.render(game_message, True, pygame.Color('Black'))
    canvas.blit(game_notice, (DISPLAY_WIDTH/2-120, 25))
    #

    #
    #=================Update Display===========================================
    pygame.display.update()

###############################################################################
# 5. Create a frame

# Initialize Objects
board = GameBoard(NUM_CHIP_WIDE, NUM_CHIP_HIGH, WIN_LENGTH)
current_gstate = GameState()

###############################################################################
# 6. Start Frame and register handlers

def main():
    """
    Initiates Frame and calls events handlers continously until program
    is exited
    """
    # Initiate Parameters
    global red_chip_stack, red_chip_outline, blue_chip_stack, blue_chip_outline, stop_b, start_b
    title = 'Connect Four'
    width = DISPLAY_WIDTH
    height = DISPLAY_HEIGHT
    pygame.init()
    # Intiate Frames per Second
    fpsClock = pygame.time.Clock()
    # Initiate Canvas for Drawing on Title
    canvas = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    # Load Necesary Images for Canvas
    #    Red Stack (Human)
    red_chip_stack = pygame.image.load('C:/Users/sillyjacob/Documents/Python Scripts/Projects/Connect 4/data/images/chips.jpg').convert_alpha() 
    red_chip_stack = pygame.transform.scale(red_chip_stack, (125,75))
    red_chip_outline = pygame.Rect((0, DISPLAY_HEIGHT-80), (135, 80))
    #    Blue Stack (AI or Human)
    blue_chip_stack = pygame.image.load('C:/Users/sillyjacob/Documents/Python Scripts/Projects/Connect 4/data/images/chips2.jpg').convert_alpha() 
    blue_chip_stack = pygame.transform.scale(blue_chip_stack, (125,75))
    blue_chip_outline = pygame.Rect((DISPLAY_WIDTH-135, DISPLAY_HEIGHT-80), (135, 80))
    #    Start/Stop Buttons
    start_b = pygame.image.load('C:/Users/sillyjacob/Documents/Python Scripts/Projects/Connect 4/data/images/Start_Button.jpg').convert_alpha()
    start_b = pygame.transform.scale(start_b, (100,60))
    stop_b = pygame.image.load('C:/Users/sillyjacob/Documents/Python Scripts/Projects/Connect 4/data/images/Stop_Button.jpg').convert_alpha()
    stop_b = pygame.transform.scale(stop_b, (100,60))
    # Run continous Loop checking for event handlers and updating screen
    running = True
    while running:
        mx,my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mdown_handler(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP: 
                mup_handler(pygame.mouse.get_pos())
        draw_handler(canvas)
        check_move()
        fpsClock.tick(60)
    pygame.quit ()
    sys.exit


###############################################################################     
# 7. Start Game
if __name__ == '__main__': main()

