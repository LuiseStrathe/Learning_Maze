# THIS IS THE ENVIRONMENT FILE FOR THE LEARNING MAZE GAME

### IMPORTS ###
import numpy as np
import random


### CLASSES ###
class Make_Map():
    
    def __init__(self, width=6, sight=2, num_mummies=1, block_rate=0.2):
        
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
        counter = 0
        solvable = False
        while ~solvable & (counter < 50):
            self.blocked_fields = sorted(np.random.choice((self.num_fields - 5), self.num_blocked, replace=False) + 2)
            self.blockers = []
            for b in self.blocked_fields:
                self.blockers.append([b // self.width, b - (b // self.width) * self.width])
            solvable, self.distance = check_map(self.width, self.blockers)
            counter += 1
        
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

        ### Info
        print()
        print(f'New Map created with {self.width ** 2} ({self.width} x {self.width}) fields.')
        print(f'{self.num_blocked} fields are blocked (X), {self.num_mummies} mummies (8) are creeping around.')
        print('You (A) start at the top left corner and have to reach the bottom right corner (E).')
        print('_____________________________________________________________')



### FUNCTIONS ###

def check_map(width, blockers): # Check if map is possible to solve
    yes = [[0, 0]]          # start at initial player position
    checked_fields = yes    # all non-blocked fields that were not yet on path
    solvable = False        # flag to indicate if map is solvable
    distance = 0            # min distance from start to end in steps

    while (solvable == False) & (len(yes) > 0):
        new = np.empty((0, 2), dtype=int)
        for x, y in yes:
            neighbors = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
            
            for xx, yy in neighbors:          
                if (xx >= 0) & (xx < width) & (yy >= 0) & (yy < width):
                    if (xx == yy) & (xx == width - 1): # exit found, is sovlable
                        solvable = True
                        break
                    elif ~(np.any(np.all(np.array([xx, yy]) == blockers, axis=1))) & \
                        ~(np.any(np.all(np.array([xx, yy]) == checked_fields, axis=1))):  
                        new = np.append(new, [[xx, yy]], axis=0) # new field reached
        
        yes = new
        checked_fields = np.append(checked_fields, new, axis=0)  
        distance += 1
        
    return solvable, distance



def find_moves(view, sight):
    
    moves = ['wait']          # list of possible moves (wait, up, down, left, right)
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



def make_move(move, player, move_targets, fields, moves):
    
    print(player)
    ### Validate move
    if move not in moves:
        print('    You cannot move there!')
        print(f'    Please select from {move_targets}')
        result = 'failed'
        
    else:
        directions = ['wait', 'up', 'down', 'left', 'right']
        target = move_targets[directions.index(move)]

        ### Check for win or loss
        if target == 'E':    
            result = 'win'
        elif target == '8':
            result = 'lose'
            
        else: 
            ### Move player
            fields[player[0], player[1]] = ' '
            
            if move == 'up':
                player = [player[0] - 1, player[1]]
            elif move == 'down':
                player = [player[0] + 1, player[1]]
            elif move == 'left':
                player = [player[0], player[1] - 1]
            elif move == 'right':
                player = [player[0], player[1] + 1]

            fields[player[0], player[1]] = 'A'  
            
            result = f'New position: {player}' 

    return player, fields, result               # result: 'win', 'failed', 'lose' or 'New position: [x, y]'



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



def move_mummies(mummies, fields):
    
    counter = -1
    stop = False
    
    print(f'Mummies are moving...')
    
    for mummy in mummies:
        counter +=1
        moves = np.full(4, 'N/A')
        x, y = mummy

        # Get options for this mummy
        xy_max = fields.shape[0] - 1
        if (x - 1 >= 0) & (x - 1 <= xy_max) & (y >= 0) & (y <= xy_max):
            moves[0] = fields[x - 1, y]
        if (x + 1 >= 0) & (x + 1 <= xy_max) & (y >= 0) & (y <= xy_max):
            moves[1] = fields[x + 1, y]
        if (x >= 0) & (x <= xy_max) & (y - 1 >= 0) & (y - 1 <= xy_max):
            moves[2] = fields[x, y - 1]
        if (x >= 0) & (x <= xy_max) & (y + 1 >= 0) & (y + 1 <= xy_max):
            moves[3] = fields[x, y + 1]
        
        if 'A' in moves:
            stop = True
            print('It\'s a trap! A mummy cought you! X.X')
                    
        else:
            # Choose the move
            move = random.sample([i for i in range(len(moves)) if moves[i] == ' '], 1)[0]
            
            # Update fields
            fields[mummy[0], mummy[1]] = ' '
            if move == []:                      # If no move is possible, stay put
                fields[mummy[0], mummy[1]] = '8'
            elif move == 0:                     # mummy moves up
                fields[x - 1, y] = '8'
            elif move == 1:                     # mummy moves down
                fields[x + 1, y] = '8'
            elif move == 2:                     # mummy moves left
                fields[x, y - 1] = '8'
            elif move == 3:                     # mummy moves right 
                fields[x, y + 1] = '8'
            
    # update mummies
    mummies = np.argwhere(fields == '8')
    if stop:
        print('You lost! X.X')
    
    return mummies, fields, stop



