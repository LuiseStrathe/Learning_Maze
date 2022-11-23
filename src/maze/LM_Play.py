# Run this to play the LEARNING MAZE GAME

### IMPORTS ###
from LM_Routines import *
from LM_Images import *


### MAIN ###

### Get input for the setup
# width, height, sight, num_mummies, block_rate = custom_input()
width = 5
sight = 3
num_mummies = 2
block_rate = 0.2

### Create a Maze
My_Map = Start_a_Game(width=width, sight=sight, num_mummies=num_mummies, block_rate=block_rate)

### Play the game
results = []
counter = 0
stop = False

while ~stop:
    create_image(My_Map.view).show()
    MyMap, result, stop = Make_a_Move(My_Map)
    results.append(result)
    counter += 1
    if stop == True: break                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               

### End of game
print('==============================================================')
print('End of game! You {result}')
print()
create_image(My_Map.fields).show()
print()
print(f'This happened in {counter} turns:')
print('     You started at [0, 0]')
for n in results:
    print('     '+n)
    
    
