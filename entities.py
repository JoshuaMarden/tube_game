from utilities import *
import random
import pickle

class StationDetails:
  def __init__(self, name, lines, adjacents, adjacents_once_removed, adjacents_twice_removed):
    self.name = name
    self.lines = lines
    self.adjacents = adjacents
    self.adjacents_once_removed = adjacents_once_removed
    self.adjacents_twice_removed = adjacents_twice_removed


class Player:
  def __init__(self, location, line, history, route):
    self.location = location
    self.line = line
    self.history = history
    self.route = route
  
  def move(self):
    prev_dest = self.route.pop(0)
    self.history.insert(0, prev_dest)
    self.location = prev_dest


class Monster(Player):
  def __init__(self, location, line, history, route):
    super().__init__(location, line, history, route)

  def random_route(self, station_classes_dict, all_stations):
    destination = random.choice(list(all_stations))
    new_route = best_route(station_classes_dict, self.location, destination)
    self.route = new_route

  def move(self, station_classes_dict, all_stations):
    if not self.route:
      self.random_route(station_classes_dict, all_stations)

    next_dest = self.route.pop(0)
    self.location = next_dest
    self.history.insert(0, self.location)



class Stalker(Monster):
  def __init__(self, location, line, history, route, stalking_effort=0):
    super().__init__(location, line, history, route)  
    self.stalking_effort = stalking_effort  

  def attempt_stalk(self, station_classes_dict, player_location, msg_list):

    station_details = station_classes_dict[self.location]
    adjacents = station_details.adjacents
    adjacents_once_removed = station_details.adjacents_once_removed
    adjacents_twice_removed = station_details.adjacents_twice_removed

    if player_location in adjacents:
      assemble_story("stalker_very_close", msg_list)
      self.route = [player_location]
      effort = random.randint(1, 5)
      self.stalking_effort += effort 

    elif player_location in adjacents_once_removed:
      assemble_story("stalker_very_close", msg_list)
      self.route = best_route(station_classes_dict, self.location, player_location)
      self.route = self.route[1:]
      effort = random.randint(1, 4)
      self.stalking_effort += effort

    elif player_location in adjacents_twice_removed:
      assemble_story("stalker_close", msg_list)
    
    if self.stalking_effort > 10:
      self.stalking_effort = 0
      self.route = [self.location]


class Lurker(Monster):
  def __init__(self, location, line, history, route):
    super().__init__(location, line, history, route)

  def attempt_lurk(self, station_classes_dict, player_location, msg_list):
    
    station_details = station_classes_dict[self.location]
    adjacents = station_details.adjacents
    adjacents_once_removed = station_details.adjacents_once_removed


    lurk_choice = random.randint(1,3)
    if lurk_choice == 1:
      try:
        self.route.insert(0, self.route[0])
      except IndexError:
        pass
    
    if player_location in adjacents:
      assemble_story("lurker_very_close", msg_list)
  
    elif player_location in adjacents_once_removed:
      assemble_story("lurker_close", msg_list)
    
