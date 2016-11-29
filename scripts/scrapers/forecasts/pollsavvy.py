from . import forecast
import json
import re
import sys
import us
import csv

CANDIDATES = {
    "Clinton": "D",
    "Trump": "R",
    "Johnson": "L",
    "McMullin": "I"
}

class PollSavvy(forecast.Forecast):
    def get_latest_predictions(self):
        rows = csv.DictReader(open("data/forecasts/raw/pollsavvy_1107.csv"))
        arr = []
        for row in rows:
            for candidate, party in CANDIDATES.items():
                state = row["state"].replace("-", "")
                if state == "US": continue
                arr.append({
                    "date": "2016-11-07",
                    "model": "pollsavvy",
                    "office": "P",
                    "state": state,
                    "party": party,
                    "candidate": candidate.upper(),
                    "win_prob": float(row["winprob_" + candidate]) / 100,
                    "est_diff": None,
                    "est_share": float(row[candidate]) / 100,
                    "est_share_2p": None
                })
        return forecast.Predictions(arr)
