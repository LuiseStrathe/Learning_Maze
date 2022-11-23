# THIS ARE THE ROUTINES FILE FOR THE LEARNING MAZE GAME

### IMPORTS ###

from LM_Environment import *
import re



### FUNCTIONS ###

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


#######################


def Start_a_Game(width, sight, num_mummies, block_rate):
    print('_____________________________________________________________')
    print()
    print('Welcome to the Mummy Maze!')
    print()
    print('You are the adventurer and you have to find your way out of the maze (field E).')
    print(f'But beware! There are {num_mummies} mummies in the maze who will try to catch you.')
    print()
    
    # Initialize map
    Start_Map = Make_Map(width=width, sight=sight, num_mummies=num_mummies, block_rate=block_rate)
    
    return Start_Map


#######################
    
    
def Make_a_Move(My_Map): 
    
    stop = False            # If True, the game has ended
    result = 'None'
    moves, move_targets = find_moves(My_Map.view, My_Map.sight)
    
    print('_____________________________________________________________')
    print()
    print('You (A) are here:')
    print(My_Map.view)
    print()
    print(f'Your turn to move!')    
    print()
    
    while result == 'None':
        
        IN = input(f'    Where do you want to go? \n    Choose from {moves} (or write quit to give up).')

        if str(IN) == 'quit':
            stop = True
            result = 'quit'
            print('You gave up. Better luck next time!')
            break
        elif IN not in moves:
            print('    You can not move this way. Try again.')
        
        else: # Player moves
            move = IN
            My_Map.player, My_Map.fields, result = make_move(move, My_Map.player, move_targets, My_Map.fields, moves)
            print(f'You moved {move} to the location {My_Map.player}.')
            
            if result == 'win':
                stop = True
                print('You found the exit! Congrats, you won!')
                break
            
            else: # Mummies move
                My_Map.mummies, My_Map.fields, stop = move_mummies(My_Map.mummies, My_Map.fields)
                print(f'The mummies moved.')
                if stop:
                    print('Game over! \nA mummy catches you.')
                    print(My_Map.fields)
                    result = 'lose'
                    break
            
                else: My_Map.view = update_view(My_Map.player, My_Map.sight, My_Map.fields)
    
    return My_Map, result, stop