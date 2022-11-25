# STREAMLIT WEB APP FOR LEARNING MAZE


### IMPORTS ####################################################################
import streamlit as st
import pandas as pd
import numpy as np
import subprocess
from PIL import Image
import pathlib
import sys
sys.path.insert(1, "/home/luise/Documents/DataScience/Projects/Learning_Maze/Learning_Maze")
from src.maze.LM_Environment import *
from src.maze.LM_Data import *


### HEAD #######################################################################
st.title('Learning Maze')
head1, head2 = st.columns(2)
head1.write('Soon to be aMazed...')
#head2.image('data/app/fav.png')
st.markdown('\n---')



### INIT GAME PARAMS ###########################################################
init1, init2 = st.columns(2) 

with init2.expander("Adapt the difficulty here"):
    
    width = st.slider('How big is the Maze?', 4, 40, 6)
    sight = st.slider('How far should you see?', 1, 4, 2)
    block_rate = st.slider('How much of the field is blocked (in %)?', 5, 30, 10)
    max_mummies = (width**2) * (1-block_rate/100) * 0.1

    num_mummies = st.slider('How many mummies are in the maze?', 1, max(2, int(max_mummies)), 2)

if 'My_Map' not in st.session_state:
    st.session_state.My_Map = []
if 'result' not in st.session_state:
    st.session_state['result'] = []   
full_map = []
map_record = []


### START NEW GAME ###
if init1.button('Start a new game!'):
    
    # create new states for this match
    for key in st.session_state.keys():
        del st.session_state[key]
 
    if 'My_Map' not in st.session_state:
        st.session_state['My_Map'] = []   
    st.session_state.My_Map = Make_Map(width, sight, num_mummies, block_rate/100)
init1.write('Please, be patient for larger mazes to load. ')
st.markdown('\n---')


### PLAY GAME ###
if st.session_state.My_Map != []:
    
    # info
    st.subheader('You have entered the Maze')
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
    im1, im2 = st.columns(2)
            
    # buttons to move
    with st.container():
        cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7 = st.columns(7)
        if cmd4.button('up'): full_map, map_record = moving('up')
    with st.container():
        cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7 = st.columns(7)
        if cmd3.button('left'): full_map, map_record = moving('left')
        if cmd4.button('wait'): full_map, map_record = moving('wait')
        if cmd5.button('right'): full_map, map_record = moving('right')
        if cmd4.button('down'): full_map, map_record = moving('down')
    
    # display info
    im1.image(st.session_state.view)     
    im2.write(f'Number of steps: {st.session_state.counter}')
    im2.write(f'Info to this map:')
    im2.write(f'{width} x {width} fields and {num_mummies} mummies')
    im2.write(f'Your last move was: {st.session_state.move}') 
    
    st.markdown('\n---')
    if st.session_state.result not in ['win', 'lose']:
        if st.button('I give up...'): 
            st.session_state.result = 'lose'
            full_map = create_image(st.session_state.My_Map.fields)
            map_record = st.session_state.My_Map 
            st.session_state.My_Map = []

    
### PRESENT RESULTS ###
if st.session_state['result'] == 'win':
    st.balloons()
    st.write('You won, cudos!')
    st.image(full_map)

    
elif st.session_state['result'] == 'lose':    
    st.write('You lost!  X_x')
    st.snowflake()
    st.image(full_map)
    


