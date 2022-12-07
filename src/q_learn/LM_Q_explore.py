# Run exploration with Q-learning

## init new Q-table with random runs
## update Q-table with random runs 


### IMPORTS ###
import sys
import time
import re
import multiprocessing as mp
from multiprocessing import Process, Pool, Queue

sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Environment import *
from src.maze.LM_Data import *
from LM_Q_Helper import *


### PARAMETERS ###
init_q = True  ### Danger Zone ###      default: False
name_q_table = 'q_table_s1_08'
path = 'Learning_Maze/data/q_learn/policies/'

batch_size = 1000     # games per epoch within max_loop_time
batch_threads = 17  # num games batches in parralel per epoch
num_epochs = 200     # epochs total

sight       = 1
wmax, wmin  = 15, 6
mmax, mmin  = 4, 0
bmax, bmin  = 25, 15
cols = ['state', 'sco_wait', 'sco_up', 'sco_down', 'sco_left', 'sco_right', 'num_wait', 'num_up', 'num_down', 'num_left', 'num_right']

patterns = [  '^_     ', '^_    [8X]',
              '^_   [8X]', 
              '^_  [X8]', 
              '^_ X', '^_X ', 
              '^_XX8', '^_XX ',
              '^_XXXX', '^_XXX[ 8]', 
              '^_8', '^_[ X]8']

print(len(patterns))

### INIT Q-TABLE ###

if init_q:
    print('Init Q-table...')
    q_table = init_q_table(sight, cols)
    print('Saving Q-table init...')
    q_table.to_csv(f'{path}{name_q_table}_explored.csv')
    q_table = pd.read_csv(f'{path}{name_q_table}_explored.csv')
else:
    print('Load Q-table', name_q_table, '...')
    q_table = pd.read_csv(f'{path}{name_q_table}_explored.csv')
    q_table.to_csv(f'{path}backup/{name_q_table}_explored_{str(datetime.now())}.csv', index=False)


# init q_table
Qs = []
for cpu in range(len(patterns)):
    Qs.append(q_table[q_table.state.str.match(patterns[cpu])])
    Qs[cpu] = Qs[cpu][cols]

print(f'   Q_table loaded: {q_table.shape}')
print(f'   cpu/patterns: {len(patterns)}')
print('   QS:', [q.shape for q in Qs])


### UPDATE Q-TABLE WITH FULLY RANDOM RUNS ###
print('Start learning...')
for counter in range(num_epochs):

    # run games
    print()
    print(f'\nRun {counter + 1} of {num_epochs}...')
    
    print('\n ########### RUN RANDOM GAMES ###########')
    print('\n Update Q-table with random runs...')
    procs = []
    Gs = [Queue() for i in range(batch_threads)]
        
    print('   Play', batch_threads, 'threads with', batch_size, 'games each...')
    for thr in range(batch_threads):
        proc = Process(target=run_random_games, args=(batch_size, wmax, wmin, sight, mmax, mmin, bmax, bmin, Gs[thr]))
        procs.append(proc)
        proc.start() 
        
    games_data = [G.get() for G in Gs]
        
    print('Processes for play threads: ', [p for p in procs])
    for proc in procs:
        proc.join() 
        proc.close()   
    
    games_data = pd.concat(games_data)  
    print ('   Games finished, # records:', len(games_data))
    #games_data = run_random_games(batch_size, wmax, wmin, sight, mmax, mmin, bmax, bmin)
    
    
    print('\n ############# UPDATE Q-TABLE ###########')
    procs = []    
    Q = [Queue() for i in range(len(patterns))]
    updated_cpu = [True for i in range(len(patterns))]
    
    for cpu in range(len(patterns)):
        
        games = games_data[games_data.state.str.match(patterns[cpu])]
        print('CPU-pattern: ', cpu, patterns[cpu], ':  Q IN', Qs[cpu].shape, '   games IN', games.shape)
        
        if len(games) > 0:
            proc = Process(target=explore_q_table, args=(Qs[cpu], games, Q[cpu]), daemon=True)
            procs.append(proc)
            proc.start()  
        else: updated_cpu[cpu] = False
    print('Processes started')
    
    for cpu in range(len(patterns)):
        if updated_cpu[cpu]:
            Qs[cpu] = Q[cpu].get()
            print('Pattern -', cpu, ':  new Q output', Qs[cpu].shape) 
               
    print('Processes ending')
    # wait until processes are finished
    for proc in procs:
        proc.join()
        proc.close()
        print('   Process finished', proc)

    print('Received data for Q-table')
    q_table = pd.concat(Qs, ignore_index=True)
  
    print('\n Save new Q-table: ', q_table.shape)
    q_table.to_csv(f'{path}{name_q_table}_explored.csv', index=False)

print('########### DONE ##############')
