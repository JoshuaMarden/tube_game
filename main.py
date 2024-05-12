from utilities import *
from entities import *

with open('lines_and_routes.pickle', 'rb') as file:
    lines_and_routes = pickle.load(file)

all_routes = get_all_routes(lines_and_routes)

all_stations = get_all_station_names(all_routes)

station_classes_dict = generate_station_data(lines_and_routes)

extracts = ["Morden", "West Sutton", "New Addington",
            "Beckenham Junction", "Orpington", "Dartford", "Beckton",
            "Barking Riverside", "Upminster", "Shenfield", "Epping",
            "Chingford", "Cheshunt", "Cockfosters", "High Barnet", 
            "Watford Junction", "Amersham",
            "Uxbridge", "Slough", "Heathrow Terminal 5", "Wimbledon"]
extract = random.choice(extracts)

starting_points = ["King's Cross & St Pancras International", "Oxford Circus", "Victoria", 
          "Bond Street", "Charing Cross", "Leicester Square", "Holborn", "Embankment",
          "Edgware Road", "Covent Garden"]
starting_point = random.choice(starting_points)

stalker_aya = Stalker(extract, None, [], [])
stalker_bob = Stalker("Hounslow Central", None, [], [])
stalker_tom = Stalker("Watford Junction", None, [], [])
stalker_tim = Stalker("Enfield Town", None, [], [])
stalker_pam = Stalker("West Croydon", None, [], [])
stalker_sam = Stalker("Wimbledon", None, [], [])

stalkers = [stalker_bob, stalker_tom, stalker_tim, stalker_pam, stalker_sam, stalker_aya]

lurker_eve = Lurker(extract, None, [], [])
lurker_rex = Lurker("South Ruislip", None, [], [])
lurker_kim = Lurker("High Barnet", None, [], [])
lurker_hal = Lurker("Enfield Town", None, [], [])
lurker_fay = Lurker("Epping", None, [], [])
lurker_ian = Lurker("Lewisham", None, [], [])

lurkers = [lurker_rex, lurker_kim, lurker_hal, lurker_fay, lurker_ian, lurker_eve]

player = Player(starting_point, None, ["start"], [])

msg_list = []

for i in range(50):
   print()

start_message = (
   f"You scurry down the steps of {starting_point}, and to your relief "
   f"you can hear a train clattering down the track towards you. You've left it "
   f"too late however, the sun is set and they're coming for you..."
)
msg_list.append(start_message)
extraction_location_msg = (f"You must make it to {extract}.")
msg_list.append(extraction_location_msg)
print_story(msg_list)

while True:
  outcome = game_turn(player, stalkers, lurkers, station_classes_dict, all_stations, msg_list, extract)

  if outcome == "caught" or outcome == "escaped":
    break

turns_survived = len(player.history) - 1
uniquie_stations = len(set(player.history)) -1 

if outcome == "escaped":
   print("\nCongratulations\n")

print(f"You survived {turns_survived} turns," 
      f"and visited {uniquie_stations} stations!")

play_again()


  