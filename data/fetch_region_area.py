import json
import requests
import pandas as pd

# Change the region code to name
mapfile = "uk-local-authority-districts-2023.hexjson"

# Define the {region:area}
object = {}

# load and process hexmap file
with open(mapfile, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
data = data["hexes"]

data = {key: value["region"] for key, value in data.items()}

with open('region_area_code_mapping', "w") as file:
    json.dump(data, file)