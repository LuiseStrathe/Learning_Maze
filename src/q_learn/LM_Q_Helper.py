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
import itertools
from itertools import product
from multiprocessing import Queue

sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Data import *
from src.maze.LM_Environment import *


### HELPER ###

def init_q_table(sight, cols):
    
    length = (2 * sight + 1) ** 2 - 1
    a_string = ' X'
    print('Listing potential states: (options, length)  _', a_string + '_', length)
    portion = list(product(a_string, repeat = length))
    states = [''.join(item) for item in portion]
    states = ['_' + s + '_' for s in states] 
    
    states = [i for i in states if i.count('X') <= length - sight]
    states = [i for i in states if i.count('8') <= length - sight * 3]
    #states = [i for i in states if i.count('E') <= 1]
    #states = [i for i in states if 'E' not in i[:length//2]]

    q_table = pd.DataFrame(columns=cols)
    q_table.state = states
    q_table.iloc[:, 1:] = 0    # initialize scores and numbers with 0
    q_table.reset_index(drop=True)
    print('Initial q_tab size: ', q_table.shape)
    
    return q_table


def get_score(counter, result, width):
    score = 0
    if result == 'win':
        min_distance = (width - 1) * 2
        score = 0.7 + (0.3 * min_distance / counter)    # max poisitive score = 1   

    return score   # score per step [-1, 1]


def get_state(My_Map):
    
    view = My_Map.view
    state = view.flatten()  
    state = '_' + ''.join(np.delete(state, len(state)//2)) + '_'  # drop middle element
    #state = np.array(([state=='X'], [state=='8'], [state=='E'])).transpose().reshape( -1)

    return state



### PLAY R (random) & Q (with q policy) ###

def r_play(width, sight, mummies, blockers):
    
    My_Map = Make_Map(width, sight, mummies, blockers)
    options = ['wait', 'up', 'down', 'left', 'right']
    result = 'start'
    counter = 0
    states = []
    actions = []
    
    while (result not in ['win', 'lose']):
        state = get_state(My_Map)
        move = random.choice(options)
        states.append(state)
        actions.append(move)
        counter += 1
        My_Map, result = make_move(My_Map, move)   
      
    ### End of game
    score = get_score(counter, result, width) 
    game_data = pd.DataFrame({'state': states, 'action': actions, 'steps': 1}).groupby(['state', 'action']).count().fillna(0).reset_index()
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


def q_play(policy, width, sight, mummies, blockers, noise_range=.5):
    My_Map = Make_Map(width, sight, mummies, blockers)

    ### Play the game
    options = ['wait', 'up', 'down', 'left', 'right']
    result = 'start'
    counter = 0
    states = []
    actions = []
    timeout_count = My_Map.width ** 2 * 20 # break endless loops
    
    policy = policy[:][:6]
    states_q = policy.state.values
    
    while (result not in ['win', 'lose']):
        state = get_state(My_Map)

        if counter > timeout_count:
            result = 'lose'
            break
        
        if state not in states_q: # if state not in q_table
            move = random.choice(options)
            
        else:  # insert random noise to not end in loops, range(-.5, .5) * noise_range
            rands = (np.random.rand(5) - .5) * noise_range   
            idx_q = np.where(states_q == state)[0]
            pvals =  policy.iloc[idx_q, 1:6].values[0]
            #pvals = np.array(policy.loc[policy.state == state, opt_qcols].values[0])
            pvals[np.isnan(pvals)] = 0
            #print('pvals: ', pvals)
            minval, maxval = min(pvals), max(pvals)
            if (maxval > 0) & (maxval > minval): 
                spread = maxval - minval
                pvals = (pvals - minval) / spread
                #print(pvals + rands)
            move = options[np.argmax(pvals + rands)]
            #print(state, '  pvals scaled: ', pvals.round(2), move)

        states.append(state)
        actions.append(move)
        counter += 1
        My_Map, result = make_move(My_Map, move)

    ### End of game
    score = get_score(counter, result, width) 

    # game_data for q_table updates
    game_data = pd.DataFrame({'state': states, 'action': actions, 'steps': 1}).groupby(['state', 'action']).count().fillna(0).reset_index()
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
    #print('Game result:', score, '# steps:', counter)
    return record, game_data


def run_random_games(n, wmax, wmin, sight, mmax, mmin, bmax, bmin,  G=None):
    games_data = pd.DataFrame(columns=['state', 'num_wait', 'num_up', 'num_down', 'num_left', 'num_right', 'score'])
    
    for i in tqdm(range(n)):
        width, sight, mummies, blockers = get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin)
        record, game_data = r_play(width, sight, mummies, blockers)
        games_data = pd.concat((games_data, game_data), axis=0, join='outer', ignore_index=True).fillna(0)
    if G is not None:
        G.put(games_data)    
    return games_data


def run_q_noise_games(n, policy, noise, wmax, wmin, sight, mmax, mmin, bmax, bmin, G=None):
    games_data = pd.DataFrame(columns=['state', 'num_wait', 'num_up', 'num_down', 'num_left', 'num_right', 'score'])
    
    wins = 0
    for i in tqdm(range(n)):
        width, sight, mummies, blockers = get_random_params(wmax, wmin, sight, mmax, mmin, bmax, bmin)
        #print('   run game ', i)
        record, game_data = q_play(policy, width, sight, mummies, blockers, noise)
        if record.result[0] == 'win': wins += 1
        games_data = pd.concat((games_data, game_data), axis=0, join='outer', ignore_index=True).fillna(0)
    print('Games won:', wins, 'out of', n, ', win rate:', round(wins / n / 100, 3), '%')       
    if G is not None: G.put(games_data)    
    return games_data


def explore_q_table(q_IN, games_data, Q):

    n = games_data.shape[0]

    for i in tqdm(range(n)):    
        
        g_data = games_data.iloc[i].values
        sta = g_data[0]

        if sta not in q_IN.state.values: 
            sta, nn_wa, nn_up, nn_do, nn_le, nn_ri, nn_score = g_data
            new_state = pd.DataFrame({
                'state': [sta], 
                'sco_wait': [nn_score], 'sco_up': [nn_score], 'sco_down': [nn_score], 'sco_left': [nn_score], 'sco_right': [nn_score],
                'num_wait': [nn_wa], 'num_up': [nn_up], 'num_down': [nn_do], 'num_left': [nn_le], 'num_right': [nn_ri]})
            
            q_IN = pd.concat((q_IN, new_state), axis=0, ignore_index=True)      
               
        else:
            q_data = q_IN[q_IN.state == sta].values[0]
            #print('   q_data: ', q_data)
            new_numbers = g_data[1:-1].astype(int)
            new_score = g_data[-1]     
            old_numbers = q_data[-5:].astype(int)
            old_scores = q_data[-10:-5]     # idx, stat, (scores, numbers)
            #print('   new_numbers: ', new_numbers, '   old_numbers: ', old_numbers)
            #print('   new_score: ', new_score, '   old_scores: ', old_scores)
            
            # update counts
            numbers = old_numbers + new_numbers
            
            # update scores
            if numbers.all() > 0:
                scores = (old_scores * old_numbers + new_score * new_numbers) / numbers  
            else:
                scores = [0, 0, 0, 0, 0]
                for n in range(5):
                    if new_numbers[n] > 0:
                        scores[n] = (old_numbers[n] * old_scores[n] + new_numbers[n] * new_score) / numbers[n]
                    else: 
                        scores[n] = int(old_scores[n])
                        
            # update q_table
            q_IN[q_IN.state == sta] = [sta, *scores, *numbers]

    # clean up q_table
    q_tab = q_IN.sort_values(by=['state'], ignore_index=True).drop_duplicates(subset=['state'], keep='first') 
    if Q is not None: Q.put(q_tab)
    return q_tab


def exploit_q_table(policy, games_data, alpha, Q=None):
    
    states = policy.state.values
    policy = policy.fillna(0)
      
    for i in tqdm(range(len(games_data))):    
        games = np.array(games_data.iloc[i].values)
        sta, score = games[0], games[-1]                   # sta, nn_wa, nn_up, nn_do, nn_le, nn_ri, nn_score 
        counts = games[1:-1]
        
        if sta not in states:  
            entry = [sta, *[score * c for c in counts]]
            entry = pd.DataFrame([entry], columns=policy.columns)
            policy = pd.concat((policy, entry), axis=0, ignore_index=True)
            
        else:   
            #print('policy before: ', policy.loc[policy.state == sta].values[0])
            q_vals = policy[policy.state == sta].values[0][1:6]  # nan, os_wa, os_up, os_do, os_le, os_ri
            #q_vals = [float(x) for x in q_vals]
            updates = np.clip([q_vals + (alpha * counts) * (score - q_vals)], 0, 1)[0]
            policy[policy.state == sta] = [sta, *updates]
        
    # clean up q_table
    policy = policy.sort_values(by=['state'], ignore_index=True).drop_duplicates(subset=['state'], keep='first')  
    #print('policy updated: ', policy.loc[policy.state == sta].values[0], '\n')
               
    if Q is not None: Q.put(policy)        
    return policy