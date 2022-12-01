# Run this to play the LEARNING MAZE GAME

### IMPORTS ###
import sys
sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Data import *
from src.maze.LM_Environment import *



### MAIN ###

### Get input for the setup
# width, height, sight, num_mummies, block_rate = custom_input()
width = 20
sight = 3
num_mummies = 3
block_rate = 0.2

### Create a Maze
My_Map = Make_Map(width=width, sight=sight, num_mummies=num_mummies, block_rate=block_rate)

### Play the game
results = []
result = 'start'
counter = 0
stop = False


while (result not in ['win', 'lose', 'failed']):
    create_image(My_Map.view).show()
    print('You can move, wait or quit.')
    move = input('Which direction do you want to go?')
    if move == 'quit':
        result = 'lose'
        print('You quit the game.')
    else:
        MyMap, result = make_move(My_Map, move)
        results.append(result)
        counter += 1
    print(move)


### End of game
print('==============================================================')
print('End of game! You {result}')
print()
create_image(My_Map.fields).show()
print()
print(f'This happened in {counter} turns:')
for n in results:
    print('     '+n)
       
    
    
def custom_input():
    max_entry_fails = 4

    # Input field size
    entry = 0
    done = False
    max_size = 100
    min_size = 4
    while (entry < max_entry_fails) & ~done:
        IN = input('What size should the maze be (height = width)? e.g. 10')
        
        if re.match('^\d+$', IN): # Check format
            if (int(IN) <= max_size) & (int(IN) <= max_size): # Check size
                print(f'Field size: {IN} x {IN}')
                done = True
                width = int(IN)
                
            else: print(f'Allowed width & height is between {min_size} and {max_size}. \nTry again.')
        else: print('Wrong input format. Tray again.')
        entry += 1     
        
    # Input view size
    entry = 0
    done = False
    while (entry < max_entry_fails) & ~done:
        IN = input(f'How far can you see in fields? e.g. 2\n \
                Choose a number between 1 and {max_size}')
        
        if re.match('^\d+$', str(IN)):
            if (int(IN) <= width) & (int(IN) >= 0): # Check format & size
                sight = int(IN)
                print(f'You can see {sight} far, so your view is {sight * 2 + 1}x{sight * 2 + 1} fields.')
                done = True
            else: print(f'Allowed view size is between 1 and {width}. \nTry again.')
        else: print(f'This didn\'t work. \nInput a number between 1 (hard) and {width} (easy).')
        entry += 1


    # Input blocked fields
    entry = 0
    done = False
    while (entry < max_entry_fails) & ~done:
        IN = input(f'How much of the map will be blocked with walls (in %)? e.g. 10\n \
                Choose a number between 0 and 25.')
        
        if re.match('^\d+$', str(IN)):
            if (int(IN) <= 25): # Check format & size
                print(f'{IN}% of the fields will have walls.')
                block_rate = int(IN) / 100
                done = True
            else: print(f'You can only chose between 0% (easy) and 25% (hard) mummies. e.g. 25 \nTry again.')
        else: print(f'This didn\'t work. \nInput a number between 0 (easy) and 25 (hard).')
        entry += 1
        
    
    # Input mummies
    entry = 0
    done = False
    max_num = int((width ** 2 * (1 - block_rate)) // 5)
    while (entry < max_entry_fails) & ~done:
        IN = input(f'How many mummies should challenge you? e.g. 2\n \
                Choose a number between 1 and {max_num}')
        
        if re.match('^\d+$', str(IN)):
            if (int(IN) <= max_num) & (int(IN) > 0): # Check format & size
                num_mummies = int(IN)
                print(f'{num_mummies} mummies will haunt you.')
                done = True
            else: print(f'You can only chose between 1 (easy) and {max_num} (hard) mummies. \nTry again.')
        else: print(f'This didn\'t work. \nInput a number between 1 (easy) and {max_num} (hard).')
        entry += 1

    return width, sight, num_mummies, block_rate