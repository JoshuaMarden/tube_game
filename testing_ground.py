from utilities import *
from entities import *

###
#Testing ground
###

with open('lines_and_routes.pickle', 'rb') as file:
    lines_and_routes = pickle.load(file)

all_routes = get_all_routes(lines_and_routes)


all_stations = get_all_station_names(all_routes)

station_classes_dict = generate_station_data(lines_and_routes)


for station, details in station_classes_dict.items():
    print(f"Station: {details.name}")
    print(f"  Lines: {details.lines}")
    print(f"  Adjacents: {details.adjacents}")
    print(f"  Once Removed Adjacents: {details.adjacents_once_removed}")
    print(f"  Twice Removed Adjacents: {details.adjacents_twice_removed}")
    print("------------------------------")


print("*********************************************")
my_route = best_route(station_classes_dict, "Holborn", "Old Street")
print(my_route)
print(len(my_route))

print(".....................................................")


print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

generic_monster = Monster("Old Street", None, [], [])
generic_monster.move(station_classes_dict, all_stations)
print(generic_monster.route)

print("------------------------------------------------------")

stalker = Stalker("Green Park", None, [], [])
stalker.attempt_stalk(station_classes_dict, "Leicester Square")
stalker.move(station_classes_dict, all_stations)
print(f"Stalker Moved to {stalker.location}")



player = Player("Leicester Square", None, [], ["Tottenham Court Road"])
player.move()
print(f"Player moved to {player.location}")

print("```````````````````````````````````````````````````````````")
lurker = Lurker("Green Park", None, [], ["Hyde Park Corner", "Knightbridge"])
lurker.attempt_lurk()
lurker.move(station_classes_dict, all_stations)