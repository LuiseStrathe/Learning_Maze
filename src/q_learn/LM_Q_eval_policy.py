# Run and test a Q-Learning policy & save record of the test


### IMPORTS ###
from datetime import datetime
from tqdm import tqdm
import sys
from multiprocessing import Process, Queue

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Environment import *
from src.maze.LM_Data import *
from LM_Q_Helper import *


### PARAMETERS ###

policy_name = 'q_table_s2_02_explored'       # name of policy or 'random'
path = 'Learning_Maze/data/q_learn/'
CPUs = 18                           # number of threads
batch_size = 10000 // CPUs           # games per thread
noise_range = .7    # pval of moves adjusted by [-.5, .5] * noise_range, default: .5

sight       = 2
wmax, wmin  = 15, 10
mmax, mmin  = 4, 1
bmax, bmin  = 25, 10

cols = ['time', 'width', 'sight', 'num_mummies', 'block_rate', 'result', 'num_steps', 'score']



### prepare ###
policy = policy_name
print('Load policy', policy_name, '...')
policy = pd.read_csv(f'{path}policies/{policy_name}.csv')
records = pd.DataFrame(columns=cols)
Rs = [Queue() for i in range(CPUs)]
procs = []


### RUN POLICY EVALUATION ###
print('Running games with policy ...')

def run_r_games(pol, batch_size, R, noise, wmax, wmin, sight, mmax, mmin, bmax, bmin):
    records = pd.DataFrame(columns=cols)
    for i in tqdm(range(batch_size)):
        width, sight, mummies, blockers = get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin)
        record, game_data = r_play(width, sight, mummies, blockers)
        records = pd.concat((records, record), axis=0, join='outer')
    R.put(records)
    return records  


def run_q_games(policy, batch_size, R, noise_range, wmax, wmin, sight, mmax, mmin, bmax, bmin):
    records = pd.DataFrame(columns=cols)
    for i in tqdm(range(batch_size)):
        width, sight, mummies, blockers = get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin)
        record, game_data = q_play(policy, width, sight, mummies, blockers, noise_range)
        records = pd.concat((records, record), axis=0, join='outer')
    R.put(records)
    return records   


for CPU in range(CPUs):
        proc = Process(target=run_q_games, args=(policy, batch_size, Rs[CPU], noise_range, wmax, wmin, sight, mmax, mmin, bmax, bmin))
        procs.append(proc)
        proc.start() 
        
records = [R.get() for R in Rs]

for proc in procs:
    proc.join() 
    proc.close()   
    
records = pd.concat(records)  


### SAVE RECORDS ###
records.to_csv(f'{path}records/{policy_name}_noi{noise_range}_{datetime.now()}.csv', index=False)
print('\nEvaluation done. Records safed.')


