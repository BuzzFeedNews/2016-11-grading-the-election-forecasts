#!/usr/bin/env python
from . import forecast 
import pandas as pd
import requests
import datetime
import us
import re
import csv
import sys

PRES_CAND_DICT = {
    "D": "CLINTON",
    "R": "TRUMP",
}

CUSTOM_STATES = {
    "Maine-2": "ME2",
    "Nebraska-2": "NE2"
}

BASE_URL = "http://table-cache1.predictwise.com/latest/"

def process_state(rows, office):
    date = forecast.today_eastern()
    arr = []
    for state in rows:
        for model in [ "overall", "markets" ]:
            if (state[0] == "Utah") and (office == "P") and (model == "overall"):
                continue
            if state[0] in CUSTOM_STATES:
                if model == "markets": continue # Table is different for ME-2/NE-2
                state_abbr = CUSTOM_STATES[state[0]]
            else:
                state_abbr = us.states.lookup(state[0]).abbr
            prob_col = 1 if model == "overall" else 2
            if state[prob_col] == None: continue
            dem_prob = float(state[prob_col].strip("%").strip(" ")) / 100
            for party in [ "D", "R" ]:
                arr.append({
                    "date": date,
                    "model": "predictwise_" + model,
                    "office": office,
                    "party": party,
                    "state": state_abbr,
                    "candidate": PRES_CAND_DICT[party] if office == "P" else None,
                    "win_prob": dem_prob if party == "D" else (1 - dem_prob),
                    "est_diff": None,
                    "est_share": None,
                    "est_share_2p": None,
                })
    return arr

def process_utah(rows, office):
    date = forecast.today_eastern()
    arr = []
    for row in rows:
        cand = row[0].split(" ")[-1].upper()
        arr.append({
            "date": date,
            "model": "predictwise_overall",
            "office": "P",
            "party": dict(TRUMP="R", CLINTON="D", MCMULLIN="I")[cand],
            "state": "UT",
            "candidate": cand,
            "win_prob": float(row[1].strip("%").strip(" ")) / 100,
            "est_diff": None,
            "est_share": None,
            "est_share_2p": None,
        })
    return arr

TABLES = [
    ("P", "table_1790.json", process_utah),
    ("P", "table_1551.json", process_state),
    ("P", "table_1776.json", process_state),
    ("S", "table_1550.json", process_state)
]

class PredictWise(forecast.Forecast):
    def get_latest_predictions(self):
        arr = []
        for office, path, processor in TABLES:
            data = requests.get(BASE_URL + path).json()["table"]
            arr += processor(data, office)
        return forecast.Predictions(arr)

    def get_historical_predictions(self):
        def reformat_date(date_str):
            return datetime.datetime.strptime(date_str, "%b%d%Y")\
                .strftime("%Y-%m-%d")
        path = "data/forecasts/raw/BuzzfeedPredictWise.xlsx"
        arr = []
        for sheetname in ("Pres", "Sen"):
            office = sheetname[0]
            df = pd.read_excel(path, sheetname=sheetname).set_index("ST")
            for state, row in df.iterrows():
                if state == "USA": continue
                for date_str, dem_pct in row.iteritems():
                    date = reformat_date(date_str)
                    for party in [ "D", "R" ]:
                        dem_prob = float(dem_pct) / 100
                        arr.append({
                            "date": date,
                            "model": "predictwise_overall",
                            "office": office,
                            "party": party,
                            "state": state,
                            "candidate": PRES_CAND_DICT[party] if office == "P" else None,
                            "win_prob": dem_prob if party == "D" else (1 - dem_prob),
                            "est_diff": None,
                            "est_share": None,
                            "est_share_2p": None,
                        })
        latest = self.get_latest_predictions()
        return forecast.Predictions(arr + latest.prediction_list)
