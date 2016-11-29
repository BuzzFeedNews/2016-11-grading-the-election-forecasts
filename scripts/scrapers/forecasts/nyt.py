import requests
from . import forecast
import random
import itertools
import json
import re
import sys

PRES_STATES = [ "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "district-of-columbia", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey", "new-mexico", "new-york", "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode-island", "south-carolina", "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west-virginia", "wisconsin", "wyoming" ]

HEADERS = { "Cookie": "NYT-BCET=1480774495%7CUD9ePFkvdXpfhpUrb1QP%2FzMtX0g%3D%7Cxo26HbPCi4VHXVXYNHuuJEEwU0jAhDVJlAtqfQdej5w%3D; NYT-S=0M88S8tFXBHA3DXrmvxADeHEdcz7izE7w6deFz9JchiAImJkOx2rgxzsV.Ynx4rkFI;" }

PRES_CAND_DICT = {
    "dem": "CLINTON",
    "rep": "TRUMP",
    "ind": "MCMULLIN"
}

def get_hash():
    url = "http://www.nytimes.com/interactive/2016/upshot/presidential-polls-forecast.html"
    html = requests.get(url, headers=HEADERS).content.decode("utf-8")
    match = re.search(r"<!-- Pipeline: [^>]+? ([0-9a-z]{40}) -->", html)
    return match.group(1)

class NYT(forecast.Forecast):
    def get_latest_predictions_president(self):
        url_hash = get_hash()
        raw = requests.get("https://static01.nyt.com/newsgraphics/2016/08/05/presidential-forecast/{0}/runtime-president.json".format(url_hash), headers=HEADERS).json()
        date = forecast.today_eastern()
        arr = []
        for state in raw["races"]:
            for party in [ "dem", "rep", "ind" ]:
                if (party == "ind") and state["state"].upper() != "UT":
                    continue
                cand_name = PRES_CAND_DICT[party]
                arr.append({
                    "date": date,
                    "forecast": "nyt",
                    "office": "P",
                    "party": party[0].upper(),
                    "state": state["state"].upper().replace("-", ""),
                    "candidate": cand_name,
                    "win_prob": state[party + "_prob"]
                })
        return forecast.Predictions(arr)

    def get_latest_predictions_senate(self):
        url_hash = get_hash()
        raw = requests.get("https://static01.nyt.com/newsgraphics/2016/08/05/presidential-forecast/{0}/runtime-senate.json".format(url_hash), headers=HEADERS).json()
        date = forecast.today_eastern()
        arr = []
        for state in raw["races"]:
            for party in [ "dem", "rep" ]:
                arr.append({
                    "date": date,
                    "forecast": "nyt",
                    "office": "S",
                    "party": party[0].upper(),
                    "state": state["state"].upper().replace("-", ""),
                    "candidate": None,
                    "win_prob": state[party + "_prob"]
                })
        return forecast.Predictions(arr)

    def get_latest_predictions(self):
        p = self.get_latest_predictions_president()
        s = self.get_latest_predictions_senate()
        return forecast.Predictions(p.prediction_list + s.prediction_list)

    def get_historical_predictions(self):
        arr = []
        for state in PRES_STATES:
            sys.stderr.write(state + "\n")
            url = "http://www.nytimes.com/interactive/2016/upshot/{0}-election-forecast.html".format(state)
            html = requests.get(url, headers=HEADERS).content.decode("utf-8")
            match = re.search(r'return ({"president":.+?});', html).group(1)
            raw = json.loads(match)
            state = raw["state"]["postal"].upper()
            for office in [ "president", "senate" ]:
                if (office == "senate") and (state == "CA"):
                    continue
                candidates = raw[office]["candidates"]
                for day in raw[office]["model"]:
                    dem_diff = day["post_mean"] / 100
                    diffs = {
                        "dem": dem_diff,
                        "rep": -dem_diff
                    }
                    for party in [ "dem", "rep", "ind" ]:
                        if (office == "senate") and (party == "ind"):
                            continue
                        candidate = candidates[party]
                        c_name = candidate["last_name"].upper()
                        c_party = candidate["party"]
                        if office == "president":
                            prob = day[party + "_prob"]
                        else:
                            if party == "dem":
                                prob = day["dem_prob"]
                            else:
                                prob = 1 - day["dem_prob"]
                        arr.append({
                            "date": day["date"],
                            "model": "nyt",
                            "office": office[0].upper(),
                            "party": c_party,
                            "state": state,
                            "candidate": c_name,
                            "win_prob": prob,
                            "est_diff": diffs.get(party),
                            "est_share": None,
                            "est_share_2p": None,
                        }) 
        return forecast.Predictions(arr)
