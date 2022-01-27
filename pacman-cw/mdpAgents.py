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


class Grid:

    # Adapted from Lab Solutions 5 (Parsons, 2017)
    # Draws a grid - where an array has one position for each element on the grid
    # Not used for any function in the map other than printing a pretty grid

    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    # Print grid
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            print
        print

    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            print
        print


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        # Record the last decision made
        self.last = Directions.STOP
        # Record locations that pacman has traveled to
        self.traveled = []
        # Record information about the locations of foods, walls and capsules
        self.food_locations = []
        self.wall_locations = []
        self.capsule_locations = []
        # Reward for different kinds of location to incentivise or discourage pacman from going to them
        self.food_reward = 10.0
        self.capsule_reward = 10.0
        self.ghost_reward = -20.0
        self.near_ignore_ghost_reward = 10.0
        self.ignore_ghost_reward = 20.0
        self.empty_reward = -5.0
        self.current_reward = -5.0
        # Number of iterations taken for value iteration
        self.iteration = 500
        # The base reward and gamma used for the Bellman Equation
        self.reward = 0.0
        self.gamma = 0.9

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        # Create map and add walls to map
        self.makeMap(state)
        self.addWallsToMap(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        # Reset the lists when a game finishes to not ruin the next round
        self.traveled = []
        self.food_locations = []
        self.wall_locations = []
        self.capsule_locations = []

        self.food_reward = 10.0

    def getMapDimension(self, corners):
        # Adapted from Lab Solutions 5 (Parsons, 2017)
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
        # Adapted from Lab Solutions 5 (Parsons, 2017)
        corners = api.corners(state)
        width, height = self.getMapDimension(corners)
        self.map = Grid(width, height)

    def addWallsToMap(self, state):
        # Adapted from Lab Solutions 5 (Parsons, 2017)
        walls = api.walls(state)
        for wall in walls:
            self.map.setValue(wall[0], wall[1], "%")

    def getSides(self, direction, north, south, east, west):
        # Take in direction looking at, and the 4 directions in order
        # Return the directions to the left and right of the input direction
        # Used to help calculate the perpendicular directions for the non-determinism of the pacman
        if direction == north:
            return east, west
        elif direction == south:
            return west, east
        elif direction == east:
            return north, south
        elif direction == west:
            return south, north

    def makeValueMap(self, state):
        # Get the most updated information about the map
        foods = api.food(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        ghosts = api.ghostStates(state)
        current_location = api.whereAmI(state)
        corners = api.corners(state)

        # Create empty dictionary to store the values of each location in format of (x, y): value
        valueMap = {}

        # Update self.traveled with the current location
        if current_location not in self.traveled:
            self.traveled.append(current_location)

        # Check if self.food_locations is up to date
        # Create dictionary to store food locations and their reward value
        # Add food locations and values to valueMap
        for food in foods:
            if food not in self.food_locations:
                self.food_locations.append(food)
        self.food_dictionary = dict.fromkeys(
            self.food_locations, self.food_reward)
        valueMap.update(self.food_dictionary)

        # Similar logic to the previous part but for capsules
        for capsule in capsules:
            if capsule not in self.capsule_locations:
                self.capsule_locations.append(capsule)
        self.capsule_dictionary = dict.fromkeys(
            self.capsule_locations, self.capsule_reward)
        valueMap.update(self.capsule_dictionary)

        # Similar logic but for walls, walls are not given values, instead they are not treated
        for wall in walls:
            if wall not in self.wall_locations:
                self.wall_locations.append(wall)
        self.wall_dictionary = dict.fromkeys(self.wall_locations, "%")
        valueMap.update(self.wall_dictionary)

        # Populate valueMap with empty locations (locations that wouldn't be covered by foods, capsules, walls)
        width, height = self.getMapDimension(corners)
        for i in range(width-1):
            for j in range(height-1):
                if (i, j) not in valueMap.keys():
                    valueMap[(i, j)] = self.empty_reward

        # Update valueMap with the location of the ghost by changing the reward to ghost_reward
        for ghost in ghosts:
            for location in valueMap.keys():
                if ghost[0] == location:
                    if ghost[1] != 1:
                        valueMap[ghost] = self.ghost_reward
                    else:
                        valueMap[ghost] = self.ignore_ghost_reward

        self.food_reward = 10000 / len(foods)

        valueMap[current_location] = self.current_reward

        return valueMap

    def calculateDirections(self, x, y, valueMap):
        # Calculate the utility of each move
        self.util_dict = {"north_util": 0.0, "south_util": 0.0,
                          "east_util": 0.0, "west_util": 0.0}

        self.valueMap = valueMap

        self.x = x
        self.y = y

        north = (self.x, self.y + 1)
        south = (self.x, self.y - 1)
        east = (self.x + 1, self.y)
        west = (self.x - 1, self.y)
        current = (self.x, self.y)

        directions = [north, south, east, west]
        # The utility of each move is 0.8 * utility of the move + 0.1 * utility of moving to the left + 0.1 * utility of moving to the right
        # If the move will hit a wall, use the utility of the current location instead
        for direction in directions:
            directionL, directionR = self.getSides(
                direction, north, south, east, west)
            util = 0
            if self.valueMap[direction] != "%":
                util += (0.8 * self.valueMap[direction])
            else:
                util += (0.8 * self.valueMap[current])
            if self.valueMap[directionL] != "%":
                util += (0.1 * self.valueMap[directionL])
            else:
                util += (0.1 * self.valueMap[current])
            if self.valueMap[directionR] != "%":
                util += (0.1 * self.valueMap[directionR])
            else:
                util += (0.1 * self.valueMap[current])
            # Assign the utility value to the dictionary to the move
            if direction == north:
                self.util_dict['north_util'] = util
            elif direction == south:
                self.util_dict['south_util'] = util
            elif direction == west:
                self.util_dict['west_util'] = util
            elif direction == east:
                self.util_dict['east_util'] = util

        return self.valueMap, self.util_dict

    def getValueOfMove(self, x, y, valueMap):

        self.valueMap = valueMap

        # Update value map with the utility of the 4 moves
        self.valueMap, self.util_dict = self.calculateDirections(
            x, y, valueMap)

        # find the max utility that is possible
        self.valueMap[(x, y)] = max(self.util_dict.values())

        return self.valueMap[(x, y)]

    def valueIteration(self, state, reward, gamma, V1):
        # iterate through the valueMap using the Bellman update
        # Get the current information on the map regarding walls, foods, capsules, ghosts, etc
        walls = api.walls(state)
        foods = api.food(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)

        ghostsStates = api.ghostStatesWithTimes(state)
        corners = api.corners(state)

        width, height = self.getMapDimension(corners)
        # Find locations near ghosts and set them to a negative value to push pacman away from them
        near_ghosts = []
        ghost_location = []
        # for larger maps, "near" is defined as with a 7x7 grid with the ghosts at the middle, with the locations closer to the ghost having a larger warning
        if width >= 8 or height >= 8:
            for ghost in ghostsStates:
                ghost_location.append(ghost[0])
                for i in range(-3, 4, 1):
                    for j in range(-3, 4, 1):
                        near_ghost = (int(ghost[0][0]+i), int(ghost[0][1]+j))
                        if near_ghost in V1:
                            if ghost[1] == 0:
                                if i == 0 and j == 0:
                                    V1[near_ghost] = self.ghost_reward
                                elif abs(i) + abs(j) == 1 and near_ghost not in ghost_location:
                                    # Use an if statement to check if near_ghost location is already chekced to avoid overwriting larger warning sign with a smaller warning
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 2, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 2
                                elif abs(i) + abs(j) == 2 and near_ghost not in ghost_location:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 4, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 4
                                elif abs(i) + abs(j) == 3 and near_ghost not in ghost_location:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 8, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 8
                                else:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.empty_reward, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.empty_reward
                                near_ghosts.append(near_ghost)
                            else:
                                # If ghost is edible, no warning, instead they are ignored
                                if i == 0 and j == 0:
                                    V1[near_ghost] = self.ignore_ghost_reward
        # for smaller maps, warning range is a 3x3 grid with ghost in the middle
        else:
            for ghost in ghostsStates:
                ghost_location.append(ghost[0])
                for i in range(-1, 2, 1):
                    for j in range(-1, 2, 1):
                        near_ghost = (int(ghost[0][0]+i), int(ghost[0][1]+j))
                        if ghost[1] == 0:
                            if i == 0 and j == 0:
                                V1[near_ghost] = self.ghost_reward
                            else:
                                V1[near_ghost] = self.ghost_reward / 2
                            near_ghosts.append(near_ghost)
                        # If ghost is edible, no warning is given, instead ignore ghost to focus on food
                        else:
                            if i == 0 and j == 0:
                                V1[near_ghost] = self.ignore_ghost_reward

        # Iterate using Bellman update, does not change value for foods, ghosts, near ghost locations and capsules
        for n in range(self.iteration):
            V = V1.copy()
            for i in range(width-1):
                for j in range(height-1):
                    if (i, j) not in walls and (i, j) not in foods and (i, j) not in ghosts and (i, j) not in near_ghosts and (i, j) not in capsules:
                        V1[(i, j)] = reward + gamma * \
                            self.getValueOfMove(i, j, V)

            n += 1

    def getPolicy(self, state, valueMap):
        current_location = api.whereAmI(state)

        self.valueMap = valueMap

        x = current_location[0]
        y = current_location[1]

        # Calculate the utility of the 4 moves
        self.valueMap, self.util_dict = self.calculateDirections(
            x, y, valueMap)
        # Find the best move (move with the largest utility)
        maxExpectedUtility = max(self.util_dict.values())
        return self.util_dict.keys()[self.util_dict.values().index(maxExpectedUtility)]

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        # print "-" * 20
        legal = api.legalActions(state)
        # Make valueMap every turn
        valueMap = self.makeValueMap(state)
        # Iterate
        self.valueIteration(state, self.reward, self.gamma, valueMap)
        # Find the best move
        best_move = self.getPolicy(state, valueMap)
        # print "best move:", best_move

        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != "%":
                    self.map.setValue(i, j, valueMap[(i, j)])

        # self.map.prettyDisplay()
        # Make the move
        if best_move == "north_util":
            self.last = Directions.NORTH
        elif best_move == "south_util":
            self.last = Directions.SOUTH
        elif best_move == "west_util":
            self.last = Directions.WEST
        elif best_move == "east_util":
            self.last = Directions.EAST
        # Random choice between the legal options.
        # raw_input("Press enter to continue...")
        return api.makeMove(self.last, legal)


class MDPAgent1(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        self.last = Directions.STOP

        self.traveled = []
        self.food_locations = []
        self.wall_locations = []
        self.capsule_locations = []

        self.food_reward = 10.0
        self.capsule_reward = 100.0
        self.ghost_reward = -1000.0
        self.near_ignore_ghost_reward = 10.0
        self.ignore_ghost_reward = 10.0
        self.empty_reward = -0.5
        self.current_reward = -5.0

        self.iteration = 500
        self.reward = -0.5
        self.gamma = 0.9

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

        self.makeMap(state)
        self.addWallsToMap(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

        self.traveled = []
        self.food_locations = []
        self.wall_locations = []
        self.capsule_locations = []

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
        for wall in walls:
            self.map.setValue(wall[0], wall[1], "%")

    def getSides(self, direction, north, south, east, west):
        if direction == north:
            return east, west
        elif direction == south:
            return west, east
        elif direction == east:
            return north, south
        elif direction == west:
            return south, north

    def makeValueMap(self, state):
        foods = api.food(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        ghosts = api.ghostStates(state)
        current_location = api.whereAmI(state)
        corners = api.corners(state)

        valueMap = {}

        if current_location not in self.traveled:
            self.traveled.append(current_location)

        for food in foods:
            if food not in self.food_locations:
                self.food_locations.append(food)
        self.food_dictionary = dict.fromkeys(
            self.food_locations, self.food_reward)
        valueMap.update(self.food_dictionary)

        for capsule in capsules:
            if capsule not in self.capsule_locations:
                self.capsule_locations.append(capsule)
        self.capsule_dictionary = dict.fromkeys(
            self.capsule_locations, self.capsule_reward)
        valueMap.update(self.capsule_dictionary)

        for wall in walls:
            if wall not in self.wall_locations:
                self.wall_locations.append(wall)
        self.wall_dictionary = dict.fromkeys(self.wall_locations, "%")
        valueMap.update(self.wall_dictionary)

        width, height = self.getMapDimension(corners)
        for i in range(width-1):
            for j in range(height-1):
                if (i, j) not in valueMap.keys():
                    valueMap[(i, j)] = self.empty_reward

        for food in self.food_locations:
            if food in self.traveled:
                valueMap[food] = self.empty_reward

        for capsule in self.capsule_locations:
            if capsule in self.traveled:
                valueMap[capsule] = self.empty_reward

        for ghost in ghosts:
            for location in valueMap.keys():
                if ghost[0] == location:
                    if ghost[1] != 1:
                        valueMap[ghost] = self.ghost_reward
                    else:
                        valueMap[ghost] = self.ignore_ghost_reward

        valueMap[current_location] = self.current_reward

        return valueMap

    def getTransition(self, x, y, valueMap):
        self.util_dict = {"north_util": 0.0, "south_util": 0.0,
                          "east_util": 0.0, "west_util": 0.0}

        self.valueMap = valueMap

        self.x = x
        self.y = y

        north = (self.x, self.y + 1)
        south = (self.x, self.y - 1)
        east = (self.x + 1, self.y)
        west = (self.x - 1, self.y)
        current = (self.x, self.y)

        directions = [north, south, east, west]

        for direction in directions:
            directionL, directionR = self.getSides(
                direction, north, south, east, west)
            util = 0
            if self.valueMap[direction] != "%":
                util += (0.8 * self.valueMap[direction])
            else:
                util += (0.8 * self.valueMap[current])
            if self.valueMap[directionL] != "%":
                util += (0.1 * self.valueMap[directionL])
            else:
                util += (0.1 * self.valueMap[current])
            if self.valueMap[directionR] != "%":
                util += (0.1 * self.valueMap[directionR])
            else:
                util += (0.1 * self.valueMap[current])

            if direction == north:
                self.util_dict['north_util'] = util
            elif direction == south:
                self.util_dict['south_util'] = util
            elif direction == west:
                self.util_dict['west_util'] = util
            elif direction == east:
                self.util_dict['east_util'] = util

        self.valueMap[current] = max(self.util_dict.values())

        return self.valueMap[current]

    def valueIteration(self, state, reward, gamma, V1):
        walls = api.walls(state)
        foods = api.food(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)

        ghostsStates = api.ghostStatesWithTimes(state)
        corners = api.corners(state)

        width, height = self.getMapDimension(corners)

        near_ghosts = []
        ghost_location = []
        if width >= 8 or height >= 8:
            for ghost in ghostsStates:
                ghost_location.append(ghost[0])
                for i in range(-3, 4, 1):
                    for j in range(-3, 4, 1):
                        near_ghost = (int(ghost[0][0]+i), int(ghost[0][1]+j))
                        if near_ghost in V1:
                            if ghost[1] == 0:
                                if i == 0 and j == 0:
                                    V1[near_ghost] = self.ghost_reward
                                elif abs(i) + abs(j) == 1 and near_ghost not in ghost_location:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 2, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 2
                                elif abs(i) + abs(j) == 2 and near_ghost not in ghost_location:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 3, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 3
                                elif abs(i) + abs(j) == 3 and near_ghost not in ghost_location:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 4, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 4
                                elif abs(i) + abs(j) == 4 and near_ghost not in ghost_location:
                                    if near_ghost in near_ghosts:
                                        V1[near_ghost] = max(
                                            self.ghost_reward / 5, V1[near_ghost])
                                    else:
                                        V1[near_ghost] = self.ghost_reward / 5
                                near_ghosts.append(near_ghost)
                            else:
                                if i == 0 and j == 0:
                                    V1[near_ghost] = self.ignore_ghost_reward
        else:
            for ghost in ghostsStates:
                ghost_location.append(ghost[0])
                for i in range(-1, 2, 1):
                    for j in range(-1, 2, 1):
                        near_ghost = (int(ghost[0][0]+i), int(ghost[0][1]+j))
                        if ghost[1] == 0:
                            if i == 0 and j == 0:
                                V1[near_ghost] = self.ghost_reward
                            elif abs(i) + abs(j) == 1 and near_ghost not in ghost_location:
                                if near_ghost in near_ghosts:
                                    V1[near_ghost] = max(
                                        self.ghost_reward / 2, V1[near_ghost])
                                else:
                                    V1[near_ghost] = self.ghost_reward / 2
                            elif abs(i) + abs(j) == 2 and near_ghost not in ghost_location:
                                if near_ghost in near_ghosts:
                                    V1[near_ghost] = max(
                                        self.ghost_reward / 3, V1[near_ghost])
                                else:
                                    V1[near_ghost] = self.ghost_reward / 3
                            elif abs(i) + abs(j) == 3 and near_ghost not in ghost_location:
                                if near_ghost in near_ghosts:
                                    V1[near_ghost] = max(
                                        self.ghost_reward / 4, V1[near_ghost])
                                else:
                                    V1[near_ghost] = self.ghost_reward / 4
                            elif abs(i) + abs(j) == 4 and near_ghost not in ghost_location:
                                if near_ghost in near_ghosts:
                                    V1[near_ghost] = max(
                                        self.ghost_reward / 5, V1[near_ghost])
                                else:
                                    V1[near_ghost] = self.ghost_reward / 5
                            near_ghosts.append(near_ghost)
                        else:
                            if i == 0 and j == 0:
                                V1[near_ghost] = self.ignore_ghost_reward

        for n in range(self.iteration):
            V = V1.copy()
            for i in range(width-1):
                for j in range(height-1):
                    if (i, j) not in walls and (i, j) not in foods and (i, j) not in ghosts and (i, j) not in near_ghosts and (i, j) not in capsules:
                        V1[(i, j)] = reward + gamma * \
                            self.getTransition(i, j, V)

            n += 1

    def getPolicy(self, state, iteratedMap):
        current_location = api.whereAmI(state)

        self.valueMap = iteratedMap

        x = current_location[0]
        y = current_location[1]

        self.util_dict = {"north_util": 0.0, "south_util": 0.0,
                          "east_util": 0.0, "west_util": 0.0}

        north = (x, y + 1)
        south = (x, y - 1)
        east = (x + 1, y)
        west = (x - 1, y)
        current = (x, y)

        directions = [north, south, east, west]

        for direction in directions:
            directionL, directionR = self.getSides(
                direction, north, south, east, west)
            util = 0
            if self.valueMap[direction] != "%":
                util += (0.8 * self.valueMap[direction])
                # print direction
                # print self.valueMap[direction]
            else:
                util += (0.8 * self.valueMap[current])
                # print current
                # print self.valueMap[current]
            if self.valueMap[directionL] != "%":
                util += (0.1 * self.valueMap[directionL])
                # print directionL
                # print self.valueMap[directionL]
            else:
                util += (0.1 * self.valueMap[current])
                # print current
                # print self.valueMap[current]
            if self.valueMap[directionR] != "%":
                util += (0.1 * self.valueMap[directionR])
                # print directionR
                # print self.valueMap[directionR]
            else:
                util += (0.1 * self.valueMap[current])
                # print current
                # print self.valueMap[current]

            if direction == north:
                self.util_dict['north_util'] = util
            elif direction == south:
                self.util_dict['south_util'] = util
            elif direction == west:
                self.util_dict['west_util'] = util
            elif direction == east:
                self.util_dict['east_util'] = util

        maxExpectedUtility = max(self.util_dict.values())
        # print(self.util_dict)
        return self.util_dict.keys()[self.util_dict.values().index(maxExpectedUtility)]

    # For now I just move randomly
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        # print "-" * 20
        legal = api.legalActions(state)
        valueMap = self.makeValueMap(state)

        self.valueIteration(state, self.reward, self.gamma, valueMap)

        best_move = self.getPolicy(state, valueMap)
        # print "best move:", best_move

        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != "%":
                    self.map.setValue(i, j, valueMap[(i, j)])

        # self.map.prettyDisplay()

        if best_move == "north_util":
            self.last = Directions.NORTH
        elif best_move == "south_util":
            self.last = Directions.SOUTH
        elif best_move == "west_util":
            self.last = Directions.WEST
        elif best_move == "east_util":
            self.last = Directions.EAST
        # Random choice between the legal options.
        # raw_input("Press enter to continue...")
        return api.makeMove(self.last, legal)
