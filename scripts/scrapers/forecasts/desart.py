#!/usr/bin/env python
from . import forecast 
import requests
import datetime
import pandas as pd
import us
import re
import csv
import sys

BASE_URL = "http://research.uvu.edu/DeSart/forecasting/"
table_pat = re.compile(r"<table width=100%.*?</table>", re.DOTALL)
row_pat = re.compile(r"<tr><td>([^<]*)</td><td align=center>([^<]*)</td><td>([^<]*)</td><td align=center>([^<]*)</td></tr>")

MISSPELLINGS = {
    "Connectiut": "Connecticut",
    "Akansas": "Arkansas"
}

clinton_shares = pd.read_excel("data/forecasts/raw/DeSart and Holbrook 11-7 State Forecasts.xlsx").set_index("State")["Clinton 2PPV"].to_dict()

def parse_page(path):
    d_match = re.search(r"(\d{2})(\d{2})", path)
    date = datetime.datetime(
        2016,
        int(d_match.group(1)),
        int(d_match.group(2))
    ).strftime("%Y-%m-%d")
    if date > "2016-11-07": return []
    html = requests.get(BASE_URL + path).content.decode("latin-1")
    table = re.search(table_pat, html).group(0)
    arr = []
    for row in re.findall(row_pat, table):
        for i in [ 0, 1 ]:
            if row[i * 2]:
                state_name = row[i*2]
                state_name = MISSPELLINGS.get(state_name, state_name)
                state_abbr = us.states.lookup(state_name).abbr
                base_prob = float(row[i * 2 + 1]) / 100
                clinton_prob = base_prob if i == 0 else 1 - base_prob
                if date == "2016-11-07":
                    clinton_share = clinton_shares[state_name] / 100
                else:
                    clinton_share = None
                arr.append({
                    "date": date,
                    "model": "desart",
                    "office": "P",
                    "state": state_abbr,
                    "party": "D",
                    "candidate": "CLINTON",
                    "win_prob": clinton_prob,
                    "est_diff": None,
                    "est_share": None,
                    "est_share_2p": clinton_share,
                })
                arr.append({
                    "date": date,
                    "model": "desart",
                    "office": "P",
                    "state": state_abbr,
                    "party": "R",
                    "candidate": "TRUMP",
                    "win_prob": 1 - clinton_prob,
                    "est_diff": None,
                    "est_share": None,
                    "est_share_2p": 1 - clinton_share if clinton_share != None else None,
                })
    return arr

class DeSartAndHolbrook(forecast.Forecast):
    def get_historical_predictions(self):
        main_page = requests.get(BASE_URL + "november.html").content\
            .decode("latin-1")
        daily_paths = re.findall(r"([a-z]+ber/\d{4}.html)", main_page)
        arr = []
        for path in daily_paths:
            arr += parse_page(path)
        return forecast.Predictions(arr)
