# STREAMLIT WEB APP FOR LEARNING MAZE


### IMPORTS ####################################################################
import streamlit as st
import emoji

from src.maze.LM_Environment import *
from src.maze.LM_Data import *


### INIT #######################################################################
if 'My_Map' not in st.session_state:
    st.session_state.My_Map = []
if 'result' not in st.session_state:
    st.session_state['result'] = []   
full_map = []
map_record = []



### HEAD #######################################################################
st.title('Learning Maze')
head1, head2 = st.columns(2)
head1.write('Soon to be aMazed...')
head2.image('data/app/fav.png')
st.markdown('\n---')



### INIT GAME PARAMS ###########################################################
init1, init2 = st.columns(2) 

with init2.expander("Adapt the difficulty here"):
    width = st.slider('How big is the Maze?', 4, 40, 6)
    sight = st.slider('How far should you see?', 1, 4, 2)
    block_rate = st.slider('How much of the field is blocked (in %)?', 5, 30, 10)
    max_mummies = (width**2) * (1-block_rate/100) * 0.1
    num_mummies = st.slider('How many mummies are in the maze?', 1, max(2, int(max_mummies)), 2)



### START NEW GAME ###
if init1.button(emoji.emojize(':alien_monster: Start a new game!')):
    # create new states for this match
    for key in st.session_state.keys():
        del st.session_state[key]
    if 'My_Map' not in st.session_state:
        st.session_state['My_Map'] = []   
    st.session_state.My_Map = Make_Map(width, sight, num_mummies, block_rate/100)
st.markdown('\n---')


### PLAY GAME ###
if st.session_state.My_Map != []:
    
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
    if 'result' not in st.session_state:
        st.session_state['result'] = 'no result, yet'

    # movemement function
    def moving(direction):
            st.session_state.move = direction
            st.session_state.counter += 1
            st.session_state.MyMap , st.session_state.result = \
                make_move(st.session_state.My_Map, st.session_state.move)     
            full_map = create_image(st.session_state.My_Map.fields)
            map_record = st.session_state.My_Map     
                    
            if st.session_state.result in ['win', 'lose']:
                st.session_state.My_Map = []
            else: st.session_state.view = create_image(st.session_state.My_Map.view)
            
            return full_map, map_record
  
 
    # insert display above buttons
    im = st.container()  
    
    # buttons to move
    cmd1, cmd2, cdm3 = st.columns(3)
    if cmd1.button(emoji.emojize(':arrow_up:  up')): full_map, map_record = moving('up')
    if cmd2.button(emoji.emojize(':arrow_left:  left')): full_map, map_record = moving('left')
    if cdm3.button(emoji.emojize(':arrow_right:  right')): full_map, map_record = moving('right')
    if cdm3.button(emoji.emojize(':stop_button:  wait')): full_map, map_record = moving('wait')
    if cmd1.button(emoji.emojize(':arrow_down:  down')): full_map, map_record = moving('down')    
    
    # quit game
    if st.session_state.result not in ['win', 'lose']:
        if st.button(emoji.emojize(':cross_mark: I give up ...')): 
            st.session_state.result = 'lose'
            full_map = create_image(st.session_state.My_Map.fields)
            map_record = st.session_state.My_Map 
            st.session_state.My_Map = []
          
    # display info
    im.image(st.session_state.view)  
    st.write(f'Info to this map:')
    st.write(f'{width} x {width} fields and {num_mummies} mummies')
    st.write(f'Number of steps: {st.session_state.counter}')
    st.write(f'Your last move was: {st.session_state.move}') 
    st.markdown('\n---')      
    
### PRESENT RESULTS ###
if st.session_state.result == 'win':
    st.balloons()
    st.success('You won, cudos!')
    st.image(full_map, caption='Full Learning Maze')
    st.session_state.result = []
    st.session_state.My_Map = []
    
elif st.session_state.result == 'lose':    
    st.error('You lost!  X_x')
    st.snow()
    st.image(full_map, caption='Full Learning Maze')
    st.session_state.result = []
    st.session_state.My_Map = []

