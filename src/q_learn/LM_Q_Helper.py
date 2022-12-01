# Q-Learning (Reinforcement Learning)¶


### IMPORTS ###

import pandas as pd
import numpy as np
import random
import sys
from itertools import product
from datetime import datetime
from tqdm import tqdm
import sys

sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Data import *
from src.maze.LM_Environment import *


### HELPER ###

def init_q_table(sight, cols):
    
    opts = ' XE8'
    length = (2 * sight + 1) ** 2 - 1
    states = ['_' + s + '_' for s in list(map(''.join, product(' X8E', repeat = length))) if (len(str(s)) == length)] 
    states = [i for i in states if i.count('E') <= 1]
    states = [i for i in states if i.count('X') <= length - sight]
    states = [i for i in states if 'E' not in i[:length//2]]
    
    q_table = pd.DataFrame(columns=cols)
    q_table['state'] = states
    q_table.iloc[:, 1:] = 0    # initialize scores and numbers with 0
    
    return q_table


def get_score(counter, result, width):
    score = 0
    if result == 'win':
        min_distance = (width - 1) ** 2
        score = min_distance ** 2 / counter    # rel speed to solve
        score = score * 100 / counter     # scale to 100 & per step
    return score 


def get_state(My_Map):
    
    view = My_Map.view
    state = view.flatten()  
    state = '_' + ''.join(np.delete(state, len(state)//2)) + '_'  # drop middle element
    #state = np.array(([state=='X'], [state=='8'], [state=='E'])).transpose().reshape( -1)

    return state



### PLAY & Q ###

def q_play(policy, width, sight, mummies, blockers, noise_range=.5):
    My_Map = Make_Map(width, sight, mummies, blockers)

    ### Play the game
    options = ['wait', 'up', 'down', 'left', 'right']
    opt_qcols = ['sco_wait', 'sco_up', 'sco_down', 'sco_left', 'sco_right']
    result = 'start'
    results = []
    counter = 0
    states = []
    actions = []
    
    while (result not in ['win', 'lose']):
        
        state = get_state(My_Map)
        if isinstance(policy, str):
            if policy == 'random':
                move = random.choice(options)
        else:
            if state not in policy['state'].values: # if state not in q_table
                move = random.choice(options)
            else:
                rands = (np.random.rand(5) - .5) * noise_range   # insert random noise to not end in loops, range(-.5, .5) * noise_range
                pvals = policy.loc[policy['state'] == state, opt_qcols].values[0]
                pvals /= max(pvals) - min(pvals)  # normalize to range of 1
                pvals = pvals + rands
                move = options[np.argmax(pvals)]
            #print(f'state: {state}, pvals: {pvals}, move: {move}')
            
        states.append(state)
        actions.append(move)
        counter += 1
        My_Map, result = make_move(My_Map, move)
        
    ### End of game
    score = get_score(counter, result, width) 

    # game_data for q_table updates
    game_data = pd.DataFrame({'state': states, 'action': actions, 'steps': 1}).groupby(['state', 'action']).count().reset_index()
    game_data = game_data.pivot_table(index='state', columns=['action'], values='steps', fill_value=0).reset_index()
    game_data['score'] = score
    for opt in options:
        game_data.rename(columns={ f'{opt}': f'num_{opt}'}, inplace=True)

    # record for performance evaluation & comparison
    record = pd.DataFrame({'time': str(datetime.now()), 
            'width': width, 
            'sight': sight, 
            'num_mummies': mummies, 
            'block_rate': int(blockers*100), 
            'result': result, 
            'num_steps': counter,
            'score': score}, index=[0])
    
    return record, game_data


def run_random_games(n, wmax, wmin, sight, mmax, mmin, bmax, bmin):
    games_data = pd.DataFrame(columns=['state', 'num_wait', 'num_up', 'num_down', 'num_left', 'num_right', 'score'])
    
    for i in tqdm(range(n)):
        width, sight, mummies, blockers = get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin)
        record, game_data = q_play('random', width, sight, mummies, blockers)
        games_data = pd.concat((games_data, game_data), axis=0, join='outer', ignore_index=True)
        
    return games_data


def update_q_table(q_table, games_data, path):
    
    # load & backup    
    q_tab = pd.read_csv(f'{path}{q_table}.csv')
    q_tab.to_csv(f'{path}backup/{q_table}_{str(datetime.now())}.csv', index=False)

    # update q_table
    for i in tqdm(range(len(games_data))):    
        
        sta, nn_wa, nn_up, nn_do, nn_le, nn_ri, nn_score = games_data.iloc[i].values
        nan, os_wa, os_up, os_do, os_le, os_ri, on_wa, on_up, on_do, on_le, on_ri = q_tab[q_tab.state == sta].values[0]
        
        if (on_wa + nn_wa) > 0: q_tab.loc[q_tab.state == sta, 'sco_wait'] = (os_wa * on_wa + nn_wa * nn_score) / (on_wa + nn_wa)
        if (on_up + nn_up) > 0: q_tab.loc[q_tab.state == sta, 'sco_up'] = (os_up * on_up + nn_up * nn_score) / (on_up + nn_up)
        if (on_do + nn_do) > 0: q_tab.loc[q_tab.state == sta, 'sco_down'] = (os_do * on_do + nn_do * nn_score) / (on_do + nn_do)
        if (on_le + nn_le) > 0: q_tab.loc[q_tab.state == sta, 'sco_left'] = (os_le * on_le + nn_le * nn_score) / (on_le + nn_le)
        if (on_ri + nn_ri) > 0: q_tab.loc[q_tab.state == sta, 'sco_right'] = (os_ri * on_ri + nn_ri * nn_score) / (on_ri + nn_ri)

        q_tab.loc[q_tab.state == sta, 'num_wait'] += nn_wa if nn_wa > 0 else 0
        q_tab.loc[q_tab.state == sta, 'num_up'] += nn_up if nn_up > 0 else 0
        q_tab.loc[q_tab.state == sta, 'num_down'] += nn_do if nn_do > 0 else 0
        q_tab.loc[q_tab.state == sta, 'num_left'] += nn_le if nn_le > 0 else 0
        q_tab.loc[q_tab.state == sta, 'num_right'] += nn_ri if nn_ri > 0 else 0
        
    q_tab.to_csv(f'{path}{q_table}.csv', index=False)
    return q_tab


