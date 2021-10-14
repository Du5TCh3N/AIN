import math

location = (9, 1)
foods = [(10, 2)]

closest_coordinate = (0,0)
closest_distance = 10000
for food in foods:
    # print(food)
    distance = math.sqrt( ((food[0]-location[0]) **2) + ((food[1]-location[1]) **2))
    if distance < closest_distance:
        closest_coordinate = food
        closest_distance = distance
target = closest_coordinate

print(closest_coordinate)

hor = target[0] - location[0]
ver = target[1] - location[1]
# legal = api.legalActions(state)
if hor > 0:
    if ver > 0:
        moves = ["WEST", "NORTH"]
    elif ver < 0:
        moves = ["WEST", "SOUTH"]
    else:
        moves = ["WEST"]
elif hor < 0:
    if ver > 0:
        moves = ["EAST", "NORTH"]
    elif ver < 0:
        moves = ["EAST", "SOUTH"]
    else:
        moves = ["EAST"]
else:
    if ver > 0:
        moves = ["NORTH"]
    elif ver < 0:
        moves = ["SOUTH"]
    else:
        moves = ["STOP"]

print(moves)

legal = ["EAST, SOUTH", "WEST"]

lst3 = [value for value in moves if value in legal]

print(lst3)