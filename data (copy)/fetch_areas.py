import json
import requests
import pandas as pd

# Change the region code to name
mapfile = "uk-local-authority-districts-2023.hexjson"

# Define the areas
areas = {}

# load and process hexmap file
with open(mapfile, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
data = data["hexes"]

data = [{'region': obj['region']} for obj in data.values()]

df = pd.DataFrame(data)
areas_codes = df['region'].unique().tolist()

for i in areas_codes:
    response = requests.get("https://findthatpostcode.uk/areas/{}.geojson".format(i))
    data = json.loads(response.text)['features'][0]['properties']['name']
    areas[i] = data

with open('areas_codes_names', "w") as file:
    json.dump(areas, file)