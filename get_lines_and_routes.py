import requests
import zipfile
import csv
from io import BytesIO, TextIOWrapper
import time
import pickle


def download_tfl_station_data():
    
    url = "https://api.tfl.gov.uk/stationdata/tfl-stationdata-detailed.zip"
    response = requests.get(url)
    response.raise_for_status()
    station_data = response.content
    return station_data


def get_london_train_lines(station_data):
       
       with zipfile.ZipFile(BytesIO(station_data)) as thezip:
        # Ensure 'Stations.csv' is the correct filename, it might be 'stations.csv'
        with thezip.open('ModesAndLines.csv') as file:
            # Convert binary stream to text stream for CSV reading
            textfile = TextIOWrapper(file, encoding='utf-8')
            csvreader = csv.reader(textfile)
            next(csvreader)  # Skip the header row if there is one
            lines_list = [rows[1] for rows in csvreader if len(rows) > 1]
            lines_list.remove("national-rail") # Only include ThamesLink National lines
            return lines_list
        

def get_station_codes_and_names(station_data):
    
  with zipfile.ZipFile(BytesIO(station_data)) as thezip:
      # Ensure 'Stations.csv' is the correct filename, it might be 'stations.csv'
      with thezip.open('Stations.csv') as file:
          # Convert binary stream to text stream for CSV reading
          textfile = TextIOWrapper(file, encoding='utf-8')
          csvreader = csv.reader(textfile)
          next(csvreader)  # Skip the header row if there is one
          station_codes_dict = {rows[0]: rows[1] for rows in csvreader if len(rows) > 1}
          return station_codes_dict
        

def get_line_routes_coded(line):

  # URL of the API endpoint
  url = f"https://api.tfl.gov.uk/Line/{line}/Route/Sequence/all?serviceTypes=regular&excludeCrowding=true"

  # Making a GET request
  response = requests.get(url)

  # Checking if the request was successful
  if response.status_code == 200:
      
    line_routes = []
    # Parse the JSON response
    data = response.json()
    line_data = data['orderedLineRoutes']
    # Loop through each route in the data
    for route in line_data:
      # Access the 'naptanIds' key which contains the list of station IDS
      station_ids = route['naptanIds']
      line_routes.append(station_ids)
    return line_routes
  else:
      print("Failed to retrieve data:", response.status_code)
      return response.status_code


def get_common_name(stop_point_id, station_names_dict):
    
    url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        common_name = data.get('commonName', 'No common name found')
        station_names_dict[stop_point_id] = common_name
        print(f"Added: {stop_point_id} : {common_name} to dict!")
        return common_name
    else:
        print(f"Failed to retrieve data for {stop_point_id}: {str(response.status_code)}")
        return response.status_code


def convert_station_codes_to_names(line_routes_coded, station_names_dict):

  line_routes_named = []
  for route in line_routes_coded:
    for index, station_code in enumerate(route):
      try:
        station_name = station_names_dict[station_code]
        route[index] = station_name
      except KeyError:
        station_name = get_common_name(station_code, station_names_dict)
        time.sleep(0.5)
        if station_name == 429: # sleep if too many requests are being sent.
          time.sleep(62)
          station_name = get_common_name(station_code, station_names_dict)
      
      route[index] = station_name
    
    line_routes_named.append(route)

  
  return line_routes_named  


# Download TFL station data
station_data = download_tfl_station_data()

# Get the station Names
try:
  with open('station_names_dict.pickle', 'rb') as file:
    station_names_dict = pickle.load(file)
except (FileNotFoundError, EOFError):
  station_names_dict = get_station_codes_and_names(station_data)
  with open('station_names_dict.pickle', 'wb') as file:
      pickle.dump(station_names_dict, file)

# Get the lines and the routes from TFL
train_lines = get_london_train_lines(station_data)

# Package lines / routes / stations into a dictionary
lines_and_routes = {}
for line in train_lines:
  # Get the routes along the lines in coded format
  line_routes_coded = get_line_routes_coded(line)
  # Swap codes for human-readable names
  line_routes_named = convert_station_codes_to_names(line_routes_coded, station_names_dict)
  # but the routes into the dictionary
  lines_and_routes[line] = line_routes_named

# Change dict values from lists of lists to sets of tuples
# (faster membership testing)
for key in lines_and_routes:
  lines_and_routes[key] = set(tuple(inner_list) for\
                                inner_list in lines_and_routes[key])

# Fix naming
new_dict = {}
for key, value in lines_and_routes.items():
  new_key = key.replace("-city", " & City").replace("-", " ")
  if any(vowel in new_key for vowel in "aeiou"):  # acronym if no vowels
    new_key = new_key.title()
  else:
    new_key = new_key.upper()
  new_key = new_key + " Line"
  new_dict[new_key] = value

lines_and_routes = new_dict  # Assign the new dictionary

# Save the dictionaries
with open('station_names_dict.pickle', 'wb') as file:
  pickle.dump(station_names_dict, file)

with open('lines_and_routes.pickle', 'wb') as file:
  pickle.dump(lines_and_routes, file)


