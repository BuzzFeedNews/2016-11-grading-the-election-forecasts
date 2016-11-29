import requests
from . import forecast
import random
import itertools
import json
import re
import sys

BASE_URL = "https://projects.fivethirtyeight.com/2016-election-forecast/"

PRES_STATES = [ "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "district-of-columbia", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey", "new-mexico", "new-york", "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode-island", "south-carolina", "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west-virginia", "wisconsin", "wyoming" ]

SENATE_STATES = [ "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maryland", "missouri", "nevada", "new-hampshire", "new-york", "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "south-carolina", "south-dakota", "utah", "vermont", "washington", "wisconsin" ]

def process_historical(data, office):
    fs = data["forecasts"]["all"]
    arr = []
    for f in fs:
        for model_name, model in f["models"].items():
            arr.append({
                "date": f["date"],
                "model": "538_" + model_name,
                "office": office,
                "state": data["state"],
                "party": f["party"],
                "candidate": f["candidate"].upper(),
                "win_prob": model["winprob"] / 100,
                "est_diff": None,
                "est_share": model["forecast"] / 100,
                "est_share_2p": None,
            })
    return arr 

def get_inline_data(url, variable):
    res = requests.get(url, params={ "r": random.random() })
    html = res.content.decode("utf-8")
    match = re.search(r"{0} = ([^;]+)".format(variable), html)
    raw = json.loads(match.group(1))
    return raw

class FiveThirtyEight(forecast.Forecast):
    def get_historical_predictions(self):
        arr = []
        for office, states in [ ("P", PRES_STATES), ("S", SENATE_STATES) ]:
            for state in states:
                sys.stderr.write("{0}: {1}\n".format(office, state))
                if office == "P":
                    url = BASE_URL + state + "/"
                else:
                    url = BASE_URL + "senate/" + state + "/"
                raw = get_inline_data(url, "race.stateData")
                p = process_historical(raw, office)
                arr += p
        return forecast.Predictions(arr)
