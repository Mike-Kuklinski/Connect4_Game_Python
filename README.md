### Connect4_Game_Python
### Author: Mike Kuklinski
### Date: 12-23-2015

# Introduction

Enclosed in this repo is code for implementing the game, Connect 4, in Python under the Pygame module.
The graphics are straight forward and allow you to play against a friend or a computer, name Nicolas.
You can also choose to go first or second. I am working on implementing difficulty settings. 

Right now the computer player(Nicolas) is pretty superior (i.e. can't beat it). The computer utilizes a blend between a Monte Carlo 
and Depth First Search (DFS) move algorithm. In early stages of the game, it will use Monte Carlo where the moves it 
'randomly' makes during the trial runs are weighted based on the success rate of the same moves made in previous trial runs. 
In later stages, it uses DFS coupled with an ongoing dictionary of games-states(key)/move(value) which it keeps track of to 
speed up the process. To help with the DFS approach, I put a timer in place for the early stages. Basically if the computer
determines the Monte Carlo approach move before 10 seconds has expired, it will utilize the remainder of time to start building the DFS dictionary.
In later stages, if it can't figure out which move to make after 15 secs, it reverts back to the Monte Carlo Method. 


##Included in this repo are the following:
- Single file python code for executing the game
- Image files associated with the chip stacks and game buttons

##Notes 
The following modules are needed for the program:
- Pygame
- copy
- random
- math
- time