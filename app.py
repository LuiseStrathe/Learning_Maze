# STREAMLIT WEB APP FOR LEARNING MAZE


### IMPORTS ####################################################################
import streamlit as st
import pandas as pd
import emoji
from datetime import datetime

from src.maze.LM_Environment import *
from src.maze.LM_Data import *


### INIT #######################################################################
if 'My_Map' not in st.session_state:
    st.session_state.My_Map = []
if 'result' not in st.session_state:
    st.session_state.result = 'empty'   
full_map = []
map_record = []



### HEAD #######################################################################
st.title('Learning Maze')
head1, head2 = st.columns(2)
head1.write('Play this game and solve the maze on many levels of difficulty!')
head1.write('Soon, human and machine performance of playing it will be compared. \n\
            Do you outperform a machine?')
head2.image('data/app/fav.png')
head2.write(emoji.emojize(':eyes: Visit my Learning Maze repo to get more background info:'))
head2.markdown('https://github.com/LuiseStrathe/Learning_Maze', unsafe_allow_html=True)

st.markdown('\n---')



### INIT GAME PARAMS ###########################################################
init1, init2 = st.columns(2) 

with init2.expander("Adapt the difficulty here"):
    width = st.slider('How big is the Maze?', 4, 40, 6)
    sight = st.slider('How far should you see?', 1, 4, 2)
    block_rate = st.slider('How much of the field is blocked (in %)?', 5, 35, 10)
    max_mummies = (width**2) * (1-block_rate/100) * 0.15
    num_mummies = st.slider('How many mummies are in the maze?', 1, max(2, int(max_mummies)), 2)


### START NEW GAME ###
if init1.button(emoji.emojize(':alien_monster: Start a new game!')):
    # create new states for this match
    for key in st.session_state.keys():
        del st.session_state[key]
    if 'My_Map' not in st.session_state:
        st.session_state['My_Map'] = [] 
    st.session_state.result = 'new'  
    st.session_state.counter = 0
    st.session_state.My_Map = Make_Map(width, sight, num_mummies, block_rate/100)    
    
st.markdown('\n---')


### PLAY GAME ###
if (st.session_state.My_Map != []) & (st.session_state.result not in ['win', 'lose']):

    # info
    st.subheader('You have entered the Maze')
    st.text('Please, be patient for larger mazes to load. ')
    with st.expander('Gampelay Info'):
        st.write('You start in the top left corner and have quickly to find your way to the exit in the bottom right!')
        st.write('The mummies move after you. If a mummy catches you, you lose! If you reach the exit, you win!')
        st.write('Hint: A mummy can move like you and detects you if you are in in an adjacent field (up, down, left or right).') 
      
    # init variables
    if 'counter' not in st.session_state:
            st.session_state['counter'] = 0
    if 'stop' not in st.session_state:
            st.session_state['stop'] = False
    if 'view' not in st.session_state:
            st.session_state['view'] = create_image(st.session_state.My_Map.view)
    if 'move' not in st.session_state:
            st.session_state['move'] = 'no move, yet'

    # movemement function
    def moving(direction):
            st.session_state.move = direction
            st.session_state.counter += 1
            st.session_state.MyMap , st.session_state.result = \
                make_move(st.session_state.My_Map, st.session_state.move)     
            if st.session_state.result in ['win', 'lose']:
                st.experimental_rerun()
            st.session_state.view = create_image(st.session_state.My_Map.view)
            
            return full_map, map_record
  
 
    # insert display above buttons
    im = st.container()  
    st.write(st.session_state.result)
    # buttons to move
    cmd1, cmd2, cdm3 = st.columns(3)
    if cmd1.button(emoji.emojize(':arrow_up:  up')): full_map, map_record = moving('up')
    if cmd2.button(emoji.emojize(':arrow_left:  left')): full_map, map_record = moving('left')
    if cdm3.button(emoji.emojize(':arrow_right:  right')): full_map, map_record = moving('right')
    if cdm3.button(emoji.emojize(':stop_button:  wait')): full_map, map_record = moving('wait')
    if cmd1.button(emoji.emojize(':arrow_down:  down')): full_map, map_record = moving('down')    
    
    # quit game
    if st.button(emoji.emojize(':cross_mark: I give up ...')): 
        st.session_state.result = 'lose'
        st.experimental_rerun()
        
    # display info
    im.image(st.session_state.view)  
    st.write(f'INFO')
    st.write(f'- {st.session_state.My_Map.width} x {st.session_state.My_Map.width} fields and {st.session_state.My_Map.num_mummies} mummies')
    st.write(f'- Number of steps: {st.session_state.counter}')
    st.write(f'- Your last move was: {st.session_state.move}') 
    st.markdown('\n---')      
    
    
    
### PRESENT RESULTS ###

def close_game():

    res1, res2 = st.columns(2)
    # show maze in full
    full_map = create_image(st.session_state.My_Map.fields)  
    res1.image(full_map, caption='Full Learning Maze')
    
    # display info about closed game
    res2.write(f'These are your stats:')
    res2.write (f'{st.session_state.result}')
    res2.text(f'- Number of steps: {st.session_state.counter}')
    res2.text(f'- Maze: {st.session_state.My_Map.width} x {st.session_state.My_Map.width} fields')
    res2.text(f'- Number of mummies: {st.session_state.My_Map.num_mummies}')
    res2.text(f'- Block rate: {st.session_state.My_Map.block_rate*100}%')
    
    st.info('Your game performance was recorded. \n\
            All records will determine human level performance and compared to machine performannce.\n\
            No personal data is used or stored.')
    
    # add to records
    data = (datetime.now(), 
            st.session_state.My_Map.width, st.session_state.My_Map.sight, 
            st.session_state.My_Map.num_mummies, st.session_state.My_Map.block_rate, 
            st.session_state.result, st.session_state.counter)
    with open('data/records/app_records_00.csv', 'a') as f:
        rec = pd.DataFrame({data}, index=[0])    
        rec.to_csv(f, header=False)    
    
    # empty states
    st.session_state.result = []
    st.session_state.My_Map = []


if st.session_state.result == 'win':
    st.balloons()
    st.success('You won, cudos!')
    close_game()

elif st.session_state.result == 'lose':    
    st.error('You lost!  X_x')
    st.snow()
    close_game()