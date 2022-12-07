# THIS IS THE ENVIRONMENT FILE FOR THE LEARNING MAZE GAME


### IMPORTS ####################################################################
import numpy as np
import random
import time


### CLASS ######################################################################

class Make_Map():
    
    def __init__(self, width=10, sight=2, num_mummies=1, block_rate=0.1):
        
        ### initialize attributes
        self.width      = int(width)
        self.block_rate = float(block_rate)
        self.num_mummies = int(num_mummies) 
        self.sight      = int(sight)
        self.num_fields = self.width ** 2
        self.num_blocked = int(self.block_rate * self.num_fields)
        fields          = np.full((self.num_fields), ' ')
        self.player     = [0, 0]
                
        ### Set blockers
        solvable = False
        while ~solvable:
            self.blocked_fields = sorted(np.random.choice((self.num_fields - 5), self.num_blocked, replace=False) + 2)
            self.blockers = []
            for b in self.blocked_fields:
                self.blockers.append([b // self.width, b - (b // self.width) * self.width])
            solvable, self.distance = check_map(self.width, self.blockers)
            if solvable: break
        
        ### Set mummies
        mummy_options = np.array(range(4, (self.num_fields - 1)))
        mummy_options = np.delete(range(self.num_fields), self.blocked_fields)
        mummy_options = mummy_options[2:-1]
        self.mummy_fields = np.random.choice(mummy_options, self.num_mummies, replace=False) 
        self.mummies = []
        for m in self.mummy_fields:
            self.mummies.append([m // self.width, m - (m // self.width) * self.width])
        
        ### Arrange the map
        fields[0]       = 'A'
        fields[-1]      = 'E'
        for field in self.blocked_fields:
            fields[field] = 'X'
        for field in self.mummy_fields:
            fields[field] = '8'
        self.fields     = fields.reshape((self.width, self.width))
        
        ### Create the initial view
        view_size = int(2 * self.sight + 1)
        view = np.full((view_size, view_size), 'X')
        view[self.sight, self.sight] = 'A'
        for h in range(self.sight + 1):
            for w in range(self.sight + 1):
                view[self.sight + h, self.sight + w] = self.fields[h, w]
        self.view = view

        #print(f'New Map created with {self.width ** 2} ({self.width} x {self.width}) fields, min {self.distance} steps.')



### HELPER FUNCTIONS ###########################################################


def get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin):
    width = random.randint(wmin, wmax)
    sight = sight
    blockers = random.randint(bmin, bmax) / 100
    
    open_fields = (width ** 2) * (1 - blockers)
    mmin, mmax = max(mmin, int(0.02 * open_fields)), min(mmax, int(0.18 * open_fields))
    if mmin > mmax:
        mmin = mmax
    mummies = random.randint(mmin, mmax)

    return width, sight, mummies, blockers


def check_map(width, blockers): # Check if map is possible to solve
    yes = [[0, 0]]          # start at initial player position
    checked_fields = yes    # all non-blocked fields that were not yet on path
    solvable = False        # flag to indicate if map is solvable
    distance = 0            # min distance from start to end in steps
    new = []
    max_distance = width * 2 * 4

    while (solvable == False) & (len(yes) > 0) & (distance < max_distance):
        distance += 1
        
        for i in range(len(yes)):
            x, y = yes[i]
            neighbors = list(([x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]))
            
            inside_maze = lambda x, y: (x >= 0) & (y >= 0) & (x < width) & (y < width)
            neighbors = [n for n in neighbors if inside_maze(n[0], n[1])]
            neighbors = [n for n in neighbors if n not in checked_fields]
            neighbors = [n for n in neighbors if n not in blockers]         
      
            for neigh in neighbors:
                if neigh == [width - 1, width - 1]:
                        solvable = True
                        break
                else:
                    new.append(neigh)
                    checked_fields.append(neigh)                

        yes = list(new)
        new =[]

    #print('Map is solvable: ', solvable, distance)        
    return solvable, distance


def find_moves(view, sight):
    
    moves = ['wait']       # list of possible moves (wait, up, down, left, right)
    move_targets = [' ']   # State of the target field for each move (empty, blocked, mummy, exit)
    
    # up, down, left, right
    move_targets.append(view[sight - 1, sight])
    if move_targets[1] in ' E8':
        moves.append('up')
    move_targets.append(view[sight + 1, sight])
    if move_targets[2] in ' E8':
        moves.append('down')
    move_targets.append(view[sight, sight - 1])
    if move_targets[3] in ' E8':
        moves.append('left')
    move_targets.append(view[sight, sight + 1])
    if move_targets[4] in ' E8':
        moves.append('right')
    
    return moves, move_targets


def move_mummies(mummies, fields):
    
    counter = -1
    stop = False
    
    #print(f'Mummies are moving...')
    
    for mummy in mummies:
        counter +=1
        
        x, y = mummy
        moves = [' ', 'ukn', 'ukn', 'ukn', 'ukn'] # to wait
        
        # Get options for this mummy
        xy_max = fields.shape[0] - 1
        if (x - 1 >= 0) & (x - 1 <= xy_max) & (y >= 0) & (y <= xy_max):
            moves[1] = fields[x - 1, y]
        if (x + 1 >= 0) & (x + 1 <= xy_max) & (y >= 0) & (y <= xy_max):
            moves[2] = fields[x + 1, y]
        if (x >= 0) & (x <= xy_max) & (y - 1 >= 0) & (y - 1 <= xy_max):
            moves[3] = fields[x, y - 1]
        if (x >= 0) & (x <= xy_max) & (y + 1 >= 0) & (y + 1 <= xy_max):
            moves[4] = fields[x, y + 1]
        
        if 'A' in moves:
            stop = True
                    
        else:
            # Choose the move
            move = random.sample([i for i in range(len(moves)) if moves[i] == ' '], 1)[0]
            
            # Update fields
            fields[x, y] = ' '
            if move == 0:                      # If no move is possible, stay put
                fields[x, y] = '8'
            elif move == 1:                     # mummy moves up
                fields[x - 1, y] = '8'
            elif move == 2:                     # mummy moves down
                fields[x + 1, y] = '8'
            elif move == 3:                     # mummy moves left
                fields[x, y - 1] = '8'
            elif move == 4:                     # mummy moves right 
                fields[x, y + 1] = '8'
            
    # update mummies
    mummies = np.argwhere(fields == '8')
    
    return mummies, fields, stop


def update_view(player, sight, fields):
    
    view_size = int(2 * sight + 1)
    start_h = player[0] - sight
    start_w = player[1] - sight
    
    view = np.full((view_size, view_size), 'X')
    
    for h in range(view_size):
        for w in range(view_size):
            id_w = start_w + w
            id_h = start_h + h
            if (id_h >= 0) & (id_w >= 0) & (id_h < fields.shape[0]) & (id_w < fields.shape[1]):
                view[h, w] = fields[(start_h + h), (start_w + w)]

    return view



### MAIN FUNCTIONS ##############################################################

def make_move(My_Map, move):
    
    moves, move_targets = find_moves(My_Map.view, My_Map.sight)
    
    ### Validate move
    if move not in moves:
        result = 'failed'
        
    else:
        directions = ['wait', 'up', 'down', 'left', 'right']
        target = move_targets[directions.index(move)]

        ### Check for win or loss
        if target == 'E':    
            result = 'win'
        elif target == '8':
            result = 'lose'
            
        else: ### Move player
            My_Map.fields[My_Map.player[0], My_Map.player[1]] = ' '
            
            if move == 'up':
                My_Map.player = [My_Map.player[0] - 1, My_Map.player[1]]
            elif move == 'down':
                My_Map.player = [My_Map.player[0] + 1, My_Map.player[1]]
            elif move == 'left':
                My_Map.player = [My_Map.player[0], My_Map.player[1] - 1]
            elif move == 'right':
                My_Map.player = [My_Map.player[0], My_Map.player[1] + 1]

            My_Map.fields[My_Map.player[0], My_Map.player[1]] = 'A'  
            
            result = f'New position: {My_Map.player}' 
    
    # move mummies
    if result not in ['win', 'lose']:
        My_Map.mummies, My_Map.fields, stop = move_mummies(My_Map.mummies, My_Map.fields)
        if stop: result = 'lose'
        
    My_Map.view = update_view(My_Map.player, My_Map.sight, My_Map.fields)

    return My_Map, result               # result: 'win', 'failed', 'lose' or 'New position: [x, y]'




