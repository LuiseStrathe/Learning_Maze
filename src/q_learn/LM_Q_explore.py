# Run exploration with Q-learning

## init new Q-table with random runs
## update Q-table with random runs // GREEDY


### IMPORTS ###
import sys
import time

sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Environment import *
from src.maze.LM_Data import *
from LM_Q_Helper import *


### PARAMETERS ###
init_q = False  ### Danger Zone ###      default: False
name_q_table = 'q_table_s1_00'
path = 'Learning_Maze/data/q_learn/policies/'

batch_size = 2000  # games per epoch within max_loop_time
num_epochs = 40      # epochs total
max_loop_time = batch_size / 2000    # minutes

sight       = 1
wmax, wmin  = 15, 13
mmax, mmin  = 4, 1
bmax, bmin  = 17, 13
cols = ['state', 'sco_wait', 'sco_up', 'sco_down', 'sco_left', 'sco_right', 'num_wait', 'num_up', 'num_down', 'num_left', 'num_right']


### INIT Q-TABLE ###


if init_q:
    print('Init Q-table...')
    q_table = init_q_table(sight, cols)
    q_table.to_csv(f'{path}{name_q_table}.csv', index=False)


### UPDATE Q-TABLE WITH FULLY RANDOM RUNS ###
print('Random runs...')

for counter in range(num_epochs):
        print(f'\nRun {counter + 1} of {num_epochs}...')
        
        timeout = time.time() + 60 * max_loop_time   # max_loop_time min from now
        while True: 
            if (time.time() < timeout):
                games_data = run_random_games(batch_size, wmax, wmin, sight, mmax, mmin, bmax, bmin)
                break
            
        print('Update Q-table with random runs...')
        q_table = update_q_table(name_q_table, games_data, path)
        print()

print('\nUpdate Q-table done. Backup safed.')
print('#############################')

