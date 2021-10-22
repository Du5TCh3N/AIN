# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import math

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP
    
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)

#GoWestAgent
#Always tries to have Pacman go west on the grid when it is possible
#If go west is not an option, go up
class GoWestAgent(Agent):

    #Create a variable to hold the last action
    def __init__(self):
        self.last = Directions.STOP
        pick = Directions.STOP
    def getAction(self, state):
        #Get the actions we can try
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        #Check if West is available, if it is, do it. Otherwise continue the same action. 
        if Directions.WEST in legal:
            return api.makeMove(Directions.WEST, legal)
        # If we can repeat the last action, do it. Otherwise make a
        # random between up or down choice.
        elif self.last in legal:
            return api.makeMove(self.last, legal) 
        else:
            if Directions.NORTH and Directions.SOUTH in legal:
                upOrDown = (Directions.NORTH, Directions.SOUTH)
                pick = random.choice(upOrDown)
            else:
                pick = random.choice(legal)
            #Change last action
            self.last = pick
            return api.makeMove(pick, legal)

#Hungry Agent
#Uses information about the location of the food to try to move towards the nearest food
class HungryAgent(Agent):
    #Create a variable to hold food locations and self location
    def __init__(self):
        self.last = Directions.STOP
        pick = Directions.STOP
        
    def getAction(self, state):
        location = api.whereAmI(state)
        foods = api.food(state)
        
        # # If there are no food targetted
        # if target != (-1, -1):
        #     # Calculate the closest food
            
        
        # # target already defined
        # else:
        #     target = target

        # Define target, closest food
        closest_coordinate = (0,0)
        closest_distance = 10000
        for food in foods:
            distance = math.sqrt( ((food[0]-location[0]) **2) + ((food[1]-location[1]) **2))
            if distance < closest_distance:
                closest_coordinate = food
                closest_distance = distance

        target = closest_coordinate    

        hor = target[0] - location[0]
        ver = target[1] - location[1]
        
        if hor > 0:
            if ver > 0:
                moves = [Directions.EAST, Directions.NORTH]
            elif ver < 0:
                moves = [Directions.EAST, Directions.SOUTH]
            else:
                moves = [Directions.EAST]
        elif hor < 0:
            if ver > 0:
                moves = [Directions.WEST, Directions.NORTH]
            elif ver < 0:
                moves = [Directions.WEST, Directions.SOUTH]
            else:
                moves = [Directions.WEST]
        else:
            if ver > 0:
                moves = [Directions.NORTH]
            elif ver < 0:
                moves = [Directions.SOUTH]
            else:
                moves = [Directions.STOP]

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # What is the target?
        print "target location: ", target

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        wanted_legal = [move for move in moves if move in legal]
        if wanted_legal:
            pick = random.choice(wanted_legal)
            self.last = pick
        else:
            pick = random.choice(legal)
            self.last = pick

        print "Wanted moves: ", moves

        
        print "choices: ", wanted_legal

        print ""
        

        return api.makeMove(pick, legal)


# Survival Agent
# Uses information about the location of the ghosts to try to stay alive as long as possible. 
# class SurvivalAgent(Agent):

# Corner Seeking Agent
# Find the 4 corners, use them to guide Pacman
class CornerSeekingAgent(Agent): 
    def __init__(self):
        self.corners_list = []
        self.target = (-1,-1)
        self.last = Directions.STOP
    def getAction(self, state):
        location = api.whereAmI(state)
        if location == self.target:
            self.target = (-1, -1)
        foods = api.food(state)
        # If corners_list is not empty:
        # check if any corner have been reached
        if self.corners_list:
            if location in self.corners_list:
                self.corners_list.remove(location)
        # If corners_list is empty:
        # Add corners to corners_list
        else: 
            self.corners_list = api.corners(state)
        
        # If there is no target
        if self.target == (-1, -1):
            # Find the nearest food and set it as target
            if foods:
                closest_coordinate = (0,0)
                closest_distance = 10000
                for food in foods:
                    distance = math.sqrt( ((food[0]-location[0]) **2) + ((food[1]-location[1]) **2))
                    if distance < closest_distance:
                        closest_coordinate = food
                        closest_distance = distance

                self.target = closest_coordinate    
            # No food nearby, set corner to be closest corner
            else: 
                # closest_coordinate = (0,0)
                # closest_distance = 10000
                # for corner in self.corners_list:
                #     distance = math.sqrt( ((corner[0]-location[0]) **2) + ((corner[1]-location[1]) **2))
                #     if distance < closest_distance:
                #         closest_coordinate = corner
                #         closest_distance = distance
                # target = closest_coordinate
                self.target = self.corners_list[0] # choose the first element
                self.corners_list.append(self.corners_list.pop(0)) # move the element to the end of the list
        else:
            if self.target in self.corners_list:
                # Find the nearest food and set it as target
                if foods:
                    closest_coordinate = (0,0)
                    closest_distance = 10000
                    for food in foods:
                        distance = math.sqrt( ((food[0]-location[0]) **2) + ((food[1]-location[1]) **2))
                        if distance < closest_distance:
                            closest_coordinate = food
                            closest_distance = distance

                    self.target = closest_coordinate    
            else:
                self.target = self.target 

        hor = self.target[0] - location[0]
        ver = self.target[1] - location[1]
            
        if hor > 0:
            if ver > 0:
                moves = [Directions.EAST, Directions.NORTH]
            elif ver < 0:
                moves = [Directions.EAST, Directions.SOUTH]
            else:
                moves = [Directions.EAST]
        elif hor < 0:
            if ver > 0:
                moves = [Directions.WEST, Directions.NORTH]
            elif ver < 0:
                moves = [Directions.WEST, Directions.SOUTH]
            else:
                moves = [Directions.WEST]
        else:
            if ver > 0:
                moves = [Directions.NORTH]
            elif ver < 0:
                moves = [Directions.SOUTH]
            else:
                moves = [Directions.STOP]

        
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        wanted_legal = [move for move in moves if move in legal]

        
        if wanted_legal:
            pick = random.choice(wanted_legal)
            
        else:
            if self.last in legal:
                pick = self.last
            else:
                pick = random.choice(legal)
                self.last = pick
        
        if self.last in legal:
            if self.last == Directions.NORTH and pick == Directions.SOUTH:
                pick = self.last
            elif self.last == Directions.SOUTH and pick == Directions.NORTH:
                pick = self.last
            elif self.last == Directions.EAST and pick == Directions.WEST:
                pick = self.last
            elif self.last == Directions.WEST and pick == Directions.EAST:
                pick = self.last
        else:
            self.last = pick

        print(location, self.target, pick, self.last, wanted_legal, foods)
        # raw_input("Press enter to continue")
        return api.makeMove(pick, legal)
        
        


# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # Where are the ghosts?
        print "Ghost positions:"
        theGhosts = api.ghosts(state)
        for i in range(len(theGhosts)):
            print theGhosts[i]

        # How far away are the ghosts?
        print "Distance to ghosts:"
        for i in range(len(theGhosts)):
            print util.manhattanDistance(pacman,theGhosts[i])

        # Where are the capsules?
        print "Capsule locations:"
        print api.capsules(state)
        
        # Where is the food?
        print "Food locations: "
        print api.food(state)

        # Where are the walls?
        print "Wall locations: "
        print api.walls(state)
        
        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.
        return api.makeMove(Directions.STOP, legal)
