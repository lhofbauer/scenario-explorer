import json
import requests
import pandas as pd

# Change the region code to name
mapfile = "uk-local-authority-districts-2023.hexjson"


# load and process hexmap file
with open(mapfile, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
data = data["hexes"]

data = {'name_code': {value["n"]:key for key, value in data.items()}
        ,'code_name': {key:value['n'] for key, value in data.items()}}


with open('local_authority_code_mapping', "w") as file:
    json.dump(data, file)

