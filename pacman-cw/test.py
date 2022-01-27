# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class MDPAgent(Agent):
    
    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        self.traveled = []
        self.food_locations = []
        self.capsule_locations = []
        self.wall_locations = []

        self.gamma = 0.9
        self.util_record = {}
        self.util = {}
        self.valueMap = {}

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

        self.makeMap(state)
        self.addWallsToMap(state)
        self.map.display()
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

        self.traveled = []
        self.food_locations = []
        self.capsule_locations = []
        self.wall_locations = []

    def getMapDimension(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]

        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1, height + 1
    
    def makeMap(self, state):
        corners = api.corners(state)
        width, height = self.getMapDimension(corners)
        self.map = Grid(width, height)
    
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    def giveLocationsValue(self, state):
        food_reward = 10
        capsule_reward = 5
        ghost_reward = -1000
        current_location_reward = -15
        empty_reward = 5

        foods = api.food(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        current_location = api.whereAmI(state)
        corners = api.corners(state)
        ghosts = api.ghosts(state)

        width, height = self.getMapDimension(corners)

        for i in range(width - 1):
            for j in range(height - 1):
                if (i, j) not in self.valueMap:
                    self.valueMap[(i, j)] = empty_reward
        
        for food in foods:
            self.valueMap[food] = food_reward
        
        for capsule in capsules:
            self.valueMap[capsule] = capsule_reward

        for ghost in ghosts:
            self.valueMap[ghost] = ghost_reward

        self.valueMap[current_location] = current_location_reward
    
    def recalculateValue(self, state):
        location = api.whereAmI(state)

        north = (location[0], location[1]+1)
        south = (location[0], location[1]-1)
        west = (location[0]-1, location[1])
        east = (location[0]+1, location[1])

        directions = [north, south, west, east]

        walls = api.walls(state)

        for direction in directions:
            if direction in walls:
                direction = location

        



    # For now I just move randomly
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        corners = api.corners(state)

        width, height = self.getMapDimension(corners)
        width -= 1
        height -= 1

        self.valueMap = self.addValueToLocations(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)
