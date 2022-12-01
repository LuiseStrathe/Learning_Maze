# Run and test a Q-Learning policy & save record of the test


### IMPORTS ###
from datetime import datetime
from tqdm import tqdm
import sys

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Environment import *
from src.maze.LM_Data import *
from LM_Q_Helper import *


### PARAMETERS ###

policy_name = 'random'       # name of policy or 'random'
path = 'Learning_Maze/data/q_learn/'
num_games = 10000

# increase if loop-error or policy not good enough
noise_range = 1.5    # pval of moves adjusted by [-.5, .5] * noise_range, default: .5

sight       = 1
wmax, wmin  = 15, 13
mmax, mmin  = 3, 1
bmax, bmin  = 14, 12

cols = ['time', 'width', 'sight', 'num_mummies', 'block_rate', 'result', 'num_steps', 'score']


### RUN POLICY EVALUATION ###
policy = policy_name
if policy_name != 'random':
    policy = pd.read_csv(f'{path}policies/{policy_name}.csv')
records = pd.DataFrame(columns=cols)

for i in tqdm(range(num_games)):
    width, sight, mummies, blockers = get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin)
    record, game_data = q_play(policy, width, sight, mummies, blockers, noise_range)
    records = pd.concat((records, record), axis=0, join='outer')

records.to_csv(f'{path}records/{policy_name}_noi{noise_range}_{datetime.now()}.csv', index=False)
print('\nEvaluation done. Records safed.')


