import pickle
import random
from InquirerPy import prompt
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from event_lines import *
import time
import textwrap
import os
import sys

def get_all_routes(lines_and_routes):
  all_routes = set()
  for routes in lines_and_routes.values():
    all_routes.update(routes)

  return all_routes

def get_all_station_names(all_routes):
  all_stations = set()
  for route in all_routes:
    for station in route:
      all_stations.add(station)
  
  return all_stations

def get_adjacent_stations(station, all_routes):
  
  adj_stations = set()

  for route in all_routes:
    if station in route:
      for index, stop in enumerate(route):
        if stop == station:
          
          if index > 0:
            adj_stations.add(route[index - 1])
          if index < len(route) - 1:
            adj_stations.add(route[index + 1])

  return adj_stations


def generate_station_data(lines_and_routes):

  from entities import StationDetails

  all_routes = get_all_routes(lines_and_routes)
  all_stations = get_all_station_names(all_routes)

  # This dict will hold lists that eventually become StationDetails instances!
  station_classes_dict = {}

  # 1
  # First loop gets all stations adjacent to current station
  for station in all_stations:
    adjacent_stations = get_adjacent_stations(station, all_routes)
    lines = set()
    for line, routes in lines_and_routes.items():
      for route in routes:
          if station in route:
              lines.add(line)
              break
    station_classes_dict[station] = [list(lines), adjacent_stations, [], []]

  # 2
  # Second loop to populates once_removed for all stations
  # (Gets stations adjacent to directly adjacent stations)
  for station, details in station_classes_dict.items():
    adjacents = details[1]
    once_removed = set()

    for adj_station in adjacents:
      if adj_station in station_classes_dict:
        adj_to_adj = station_classes_dict[adj_station][1]
        once_removed.update(# only adds if stop not already used
          s for s in adj_to_adj if\
            s not in adjacents and\
              s != station
          )
    details[2] = once_removed

  # 3
  # Third loop to populate twice_removed for all stations
  # (Basically, any that are 3 stops from current station)
  for station, details in station_classes_dict.items():
    adjacents = details[1]
    once_removed = details[2]
    twice_removed = set()

    for once_station in once_removed:
      if once_station in station_classes_dict:
        adj_to_once_removed = station_classes_dict[once_station][1]
        twice_removed.update( # only adds if stop not already used
          s for s in adj_to_once_removed if\
            s not in adjacents and\
              s not in once_removed and\
                s != station
          )
    details[3] = twice_removed
  
  # Convert each station's data from lists to StationDetails instances!
  for station, details in station_classes_dict.items():
    lines, adjacents, adjacents_once_removed, adjacents_twice_removed = details
    station_classes_dict[station] = StationDetails(station, lines, adjacents, adjacents_once_removed, adjacents_twice_removed)

  return station_classes_dict



def random_route(station_classes_dict, starting_at, ending_at="Mars", iterations=100, memory=10):

  current = starting_at
  history = []
  route = []

  for _ in range(iterations):
    
    # Get possible next stops
    details = station_classes_dict[current]
    adjacents = details.adjacents

    # Remove from list if stop was recently visited
    adjacents = adjacents - set(history)
    
    # If this leaves no stops to visit, clear visit history
    if len(adjacents)==0:
      history = []
      adjacents = details.adjacents

    # Chose from possible stops/directions
    next_stop = random.choice(list(adjacents))
    
    # Update route / history / current stop
    history.insert(0, current)
    route.append(current)
    current=next_stop

    # Keep history memory short
    if len(history) > memory:
      history = history[0:memory+1]

    # Terminate pathing if we wanted to reach this station
    if route[-1] == ending_at:
      break
  
  return(route)


def best_route(station_classes_dict, starting_at, ending_at="Mars", iterations=100, memory=10):

  best_route = random_route(station_classes_dict, starting_at, ending_at, iterations, memory)

  for _ in range(100):
    new_route = random_route(station_classes_dict, starting_at, ending_at, iterations, memory)
    
    if len(new_route) < len(best_route):
      best_route = new_route
      iterations = len(best_route)
  
  return(best_route[:-1])


def assemble_story(event, msg_list):

  random_line = random.choice(event_lines[event])
  msg_list.append(random_line)

  if event == "caught":
    random_line = random.choice(event_lines["dead"])
    msg_list.append(random_line)


def print_story(msg_list):
  char_delay = 0.03
  msg_delay = 0.7
  line_width = 80

  train_art = (
              "________   ______________________>__\n"\
              " []_[]||[| |]||[]_[]_[]|||[]_[]_[]||[|\n"\
              " ===o-o==/_\==o-o======o-o======o-o==/______\n"\
              ":::::::::::::::::::::::::::::::::::::::::::"
              )

  for message in msg_list:
    if message == "...":
      print(train_art)
      print()
      time.sleep(msg_delay)
    else:
      wrapped_lines = textwrap.wrap(message, width=line_width)
      for line in wrapped_lines:
        for char in line:
          print(char, end='', flush=True)
          time.sleep(char_delay)
        print() 
      time.sleep(msg_delay)
      print()
  
  msg_list.clear()
  

def ask_player_for_dest(player, station_classes_dict):
  player_location = player.location
  station = station_classes_dict[player_location]
  ajacent_stations = station.adjacents
  choices_list = list(ajacent_stations) + ["Stay put, and get the next train"]
  
  question = {
    "type": "list",
    "message": "Which stop do you want to travel to:",
    "choices": choices_list,
    "default": None,
    }
  
  result = prompt(question)

  return result[0]
  


def player_will_be_seen(player, monster):

  # Check if both route lists and history lists have at least one element
  if len(monster.history) > 1 and len(player.history) > 1:
    if player.route[0] == monster.history[1] and monster.location == player.history[0]:
      return True
  return False
  
def player_wil_be_caught(player, monster):
  if player.route[0] == monster.location:
    return True
  else:
    return False


def game_turn(player, stalkers, lurkers, station_classes_dict, all_stations, msg_list, extract):

  all_monsters = lurkers + stalkers

  user_input = ask_player_for_dest(player, station_classes_dict)
  print()
  if "Stay" in user_input:
    player.route = [player.location]
  else:
    player.route = [user_input]

  player_seen = False
  player_caught = False
  for m in all_monsters:
    if player_wil_be_caught(player, m):
      player_caught = True
      break
    if player_will_be_seen(player, m):
      player_seen = True
    

  for stalker in stalkers:
    if player_seen:
      route_to_player = best_route(station_classes_dict, stalker.location, player.location)
      stalker.route = route_to_player
    stalker.attempt_stalk(station_classes_dict, player.location, msg_list)
    stalker.move(station_classes_dict, all_stations)

  for lurker in lurkers:
    if player_seen:
      route_to_player = best_route(station_classes_dict, stalker.location, player.location)
      lurker.route = route_to_player
    lurker.attempt_lurk(station_classes_dict, player.location, msg_list)
    lurker.move(station_classes_dict, all_stations)
  
  locality_warning_messages = msg_list[:]
  msg_list.clear()

  if player.route[0] == extract and not player_caught:
    escape_msg = ("You reach your destination. You pull your coat about you and"
    " fly up the steps into the empty streets. Soon you are lost to the shadows.")
    assemble_story("pull_away", msg_list)
    msg_list.append("...")
    assemble_story("pull_in", msg_list)
    msg_list.append(escape_msg)
    print_story(msg_list)
    player.move()
    return "escaped"


  if "Stay put" in user_input:
    msg_list.append("The train departs without you.")
    msg_list.append("...")
    msg_list.append("Another train clatters down the line towards you.")
    msg_list = msg_list + locality_warning_messages
  elif player.route[0] == extract:
    assemble_story("pull_away", msg_list)
    msg_list.append("...")
    assemble_story("pull_in", msg_list)
    msg_list.append(escape_msg)
  else:
    assemble_story("pull_away", msg_list)
    msg_list.append("...")
    assemble_story("pull_in", msg_list)
    msg_list.append(f"You are now at {user_input}")
    msg_list = msg_list + locality_warning_messages

  try:
    for m in all_monsters:
      if player_seen:
        msg_list.clear()
        assemble_story("pull_away", msg_list)
        msg_list.append("...")
        assemble_story("seen", msg_list)
        msg_list.append("...")
        assemble_story("pull_in", msg_list)
        msg_list = msg_list + locality_warning_messages
        break

      if player_wil_be_caught(player, m) and \
        player.route[0] != player.location:
        msg_list.clear()
        assemble_story("pull_away", msg_list)
        msg_list.append("...")
        assemble_story("pull_in", msg_list)
        assemble_story("caught", msg_list)
        print_story(msg_list)
        player.move()
        return "caught"
        
      elif player_wil_be_caught(player, m):
        msg_list.clear()
        msg_list.append("The train departs without you.")
        msg_list.append("...")
        msg_list.append("Another train clatters down the line towards you.")
        assemble_story("caught", msg_list)
        print_story(msg_list)
        player.move()
        return "caught"
  
  except IndexError:
    # This will occur on first go when history empty
    pass
  
  print_story(msg_list)

  player.move()


def restart_program():
    """Restarts the current program"""
    os.execv(sys.executable, ['python'] + sys.argv)

def play_again():
    play_again = False 
    play_again = inquirer.confirm(message="Would you like to play again?",\
                                  default=True).execute()
    if play_again:
        restart_program






  


  

  

