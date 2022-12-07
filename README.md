# Learning_Maze

<br> 
 The Learning Maze is a game to be played by humans. Also, I let an algorithm play it and compare the results from model to human level.
<br> 

----

<br> 
Link to web app (Streamlit):

https://luisestrathe-learning-maze-app-kung98.streamlit.app/
<br><br> 

*Work in progress:*

*The goal is to have humans and ml algorithms play the same maze. Finally, I will compare the performance of some model to human level.*
*Right now, models are trained and evaluated.*

<br> 

----
<br>

FEATURES
-----------------------------------------

- The maze can be configured by size (always quadratic), ratio of walls, number of opponents and how much the agent (player) can see around her.
- The agent can move in the maze up, down, left and right or wait.
- Every map is solvable. The agent can always reach the goal. Yet, opponents might make it impossible to pass.
- scoring will be based on 
    - success rate
    - number of steps taken (incl. waiting) in relation to the shortest path
    - the difficulty level
- The difficulty level will be based a regressor trained on the data of the human players. [0 (almost impossible not to win) - 100 (almost impossible to win)]

<br> 

----
<br>

MODEL PERFORMANCE
-----------------------------------------

**Human perfornance:**

- The human players can play on the web app. Their performance is stored in a Supabase cloud database.

    WIN RATE: **57 %**

<br>

**Model perfornance:**

- *Agents are acting in random generated maps and see 1 field far*

- *Performance test over 10 tsd. games each*

<br>

1) The **random baseline model** is randomly choosing a move. It is not trained at all. It is just a baseline to compare the performance of the other models to.

    WIN RATE:  **2 %** 



    

2) The **explored q-learning model** uses a q-table to choose a move. To not get stuck in a loop, the pvalues additionally are randomly adjusted within a certain range. Nevertheless, the distribution of learned moves remains.

    The pvalues for the moves come from fully random exploration (as in baseline) returning a match score. 

    WIN RATE:  **46 %**

<br> 

----
<br>

REPO STRUCTURE
-----------------------------------------

    
    |── data
    │   ├── app             <- images and reports from the web app users
    │   ├── input           <- images for maze map generation
    │   ├── records         <- records of game results
    │   └── tmp             <- temporary files
    │
    ├── src                 <- Source code for use in this project.
    │   ├── LM_Run.py       <- Run maze locally
    │   └── maze            <- Environment of the maze
    │       ├── LM_Data.py  <- Scripts to download or generate data       
    │       └── LM_Environment.py
    │                       <- Map class and evnrioment functions 
    │
    │── app.py              <- Streamlit web app
    │
    ├── LICENSE             <- MIT License
    ├── README   
    └── requirements.txt   