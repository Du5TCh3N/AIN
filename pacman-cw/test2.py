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
    
    '''
    Using map information, the MDP Agent calculate the utilities of locations. In order for Pacman to make the best decisions. 

    Values are updated every time a move is taken, to check if states have changed (food was eaten, or ghost moved). 

    Therefore, the bigger the map, the longer it takes to iterate through and check for every state change. 
    '''

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # lists storing the locations traversed by Pacman
        self.traversed = []
        # list storing the food locations, locations are removed after being visited/eaten
        self.food_locations = []
        # list storing the capsule locations, locations are removed after being visited/eaten
        self.capsule_locations = []
        # list storing the wall locations
        self.wall_locations = []
        # map storing the utility value of each location
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

        # reset lists and valueMap
        self.traversed = []
        self.food_locations = []
        self.capsule_locations = []
        self.wall_locations = []
        self.valueMap = {}

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

    #Place walls into map grid
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '#')

    def addValueToLocations(self, state):
        FOOD_REWARD = 10
        WALL_REWARD = "#"
        CAPSULE_REWARD = 5
        GHOST_REWARD = -1000
        EMPTY_REWARD = 5

        foods = api.food(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        current_location = api.whereAmI(state)
        corners = api.corners(state)

        if current_location not in self.traversed:
            self.traversed.append(current_location)

        # Add locations generated by api for foods, walls and capsules to their respective storing list
        for food in foods:
            if food not in self.food_locations:
                self.food_locations.append(food)
        
        for wall in walls:
            if wall not in self.wall_locations:
                self.wall_locations.append(wall)

        for capsule in capsules:
            if capsule not in self.capsule_locations:
                self.capsule_locations.append(capsule)

        # Give food, wall and capsule values
        self.food_dictionary = dict.fromkeys(self.food_locations, FOOD_REWARD)
        self.wall_dictionary = dict.fromkeys(self.wall_locations, WALL_REWARD)
        self.capsule_dictionary = dict.fromkeys(self.capsule_locations, CAPSULE_REWARD)

        self.valueMap.update(self.food_dictionary)
        self.valueMap.update(self.wall_dictionary)
        self.valueMap.update(self.capsule_dictionary)

        width, height = self.getMapDimension(corners)

        for i in range(width - 1):
            for j in range(height - 1):
                if (i, j) not in self.valueMap:
                    self.valueMap[(i, j)] = EMPTY_REWARD

        for food in self.food_locations:
            if food in self.traversed:
                self.valueMap[food] = FOOD_REWARD

        for capsule in self.capsule_locations:
            if capsule in self.traversed:
                self.valueMap[capsule] = CAPSULE_REWARD

        ghosts = api.ghosts(state)

        for ghost in ghosts:
            ghost = (int(ghost[0]), int(ghost[1]))
            if ghost in self.valueMap.keys():
                self.valueMap[ghost] = GHOST_REWARD

        return self.valueMap

    def calculateUtility(self, location):
        north = (location[0], location[1]+1)
        south = (location[0], location[1]-1)
        west = (location[0]-1, location[1])
        east = (location[0]+1, location[1])

        self.util_dict = {north: 0.0, south:0.0, east:0.0, west:0.0}

        for direction in self.util_dict.keys():
            if direction in self.wall_dictionary:
                self.util_dict[direction] = self.valueMap[location]
            else:
                self.util_dict[direction] = self.valueMap[direction]

        ExpectedUtility = []
        # Add each potential utility, for example the expected utility of going north is 0.8 * the value for north + 0.1 * value for west + 0.1 * value for east
        ExpectedUtility.append(0.8 * self.util_dict[north] + 0.1 * self.util_dict[west] + 0.1 * self.util_dict[east])
        ExpectedUtility.append(0.8 * self.util_dict[west] + 0.1 * self.util_dict[south] + 0.1 * self.util_dict[north])
        ExpectedUtility.append(0.8 * self.util_dict[south] + 0.1 * self.util_dict[east] + 0.1 * self.util_dict[west])
        ExpectedUtility.append(0.8 * self.util_dict[east] + 0.1 * self.util_dict[north] + 0.1 * self.util_dict[south])

        MaxExpectedUtility = max(ExpectedUtility)

        self.valueMap[location] = MaxExpectedUtility

        return self.valueMap[location]
    
    def valueIteration(self, state, reward, gamma):
        foods = api.food(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)
        corners = api.corners(state)

        width, height = self.getMapDimension(corners)
        width -= 1
        height -= 1

        if (gamma < 0 or gamma >= 1):
            # gamma out of bound
            raise ValueError("Gamme out of bound")

        for n in range(100):
            valueMapCopy = self.valueMap.copy()
            for x in range(width):
                for y in range(height):
                    if (x, y) not in walls and (x, y) not in foods and (x, y) not in ghosts and (x, y) not in capsules:
                        valueMapCopy[(x, y)] = reward + gamma * self.calculateUtility((x, y))
        
            n += 1

    def getPolicy(self, state):
        location = api.whereAmI(state)

        north = (location[0], location[1]+1)
        south = (location[0], location[1]-1)
        west = (location[0]-1, location[1])
        east = (location[0]+1, location[1])

        self.util_dict = {north: 0.0, south:0.0, east:0.0, west:0.0}

        for direction in self.util_dict.keys():
            if direction in self.wall_dictionary:
                self.util_dict[direction] = self.valueMap[location]
            else:
                self.util_dict[direction] = self.valueMap[direction]

        ExpectedUtility = [0.0, 0.0, 0.0, 0.0]
        # Add each potential utility, for example the expected utility of going north is 0.8 * the value for north + 0.1 * value for west + 0.1 * value for east
        ExpectedUtility[0] += (0.8 * self.util_dict[north] + 0.1 * self.util_dict[west] + 0.1 * self.util_dict[east])
        ExpectedUtility[1] += (0.8 * self.util_dict[west] + 0.1 * self.util_dict[south] + 0.1 * self.util_dict[north])
        ExpectedUtility[2] += (0.8 * self.util_dict[south] + 0.1 * self.util_dict[east] + 0.1 * self.util_dict[west])
        ExpectedUtility[3] += (0.8 * self.util_dict[east] + 0.1 * self.util_dict[north] + 0.1 * self.util_dict[south])

        MaxExpectedUtility = max(ExpectedUtility)

        move_index = ExpectedUtility.index(MaxExpectedUtility)

        if move_index == 0:
            return "north"
        elif move_index == 1:
            return "west"
        elif move_index == 2:
            return "south"
        elif move_index == 3:
            return "east"

    def getAction(self, state):
        legal = api.legalActions(state)
        corners = api.corners(state)

        width, height = self.getMapDimension(corners)
        width -= 1
        height -= 1

        self.valueMap = self.addValueToLocations(state)

        self.valueIteration(state, 0, 0.6)

        best_move = self.getPolicy(state)
        print "best move: ", best_move
        print "------------------------------"

        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != "WALL":
                    self.map.setValue(i, j, self.valueMap[(i, j)])
        self.map.prettyDisplay()

        if best_move == "north":
        	return api.makeMove(Directions.NORTH, legal)

        if best_move == "south":
            return api.makeMove(Directions.SOUTH, legal)

        if best_move == "east":
            return api.makeMove(Directions.EAST, legal)

        if best_move == "west":
            return api.makeMove(Directions.WEST, legal)

        