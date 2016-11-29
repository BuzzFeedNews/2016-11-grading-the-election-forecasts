import requests
from . import forecast
import random
import datetime
import itertools
import json
import re
import sys
import us
import csv
import itertools
from operator import itemgetter

BASE_URL = "https://elections.dailykos.com/app/data/"

PRES_CAND_DICT = {
    "D": "CLINTON",
    "R": "TRUMP",
}
def get_data(filename):
    raw = requests.get(BASE_URL + filename).content.decode("utf-8")
    core = " = ".join(raw.split(" = ")[2:])
    return json.loads(core)

clinton_vote_shares = dict((row["date"], row)
    for row in csv.DictReader(open("data/forecasts/raw/clinton_vote_forecasts_dailykos.csv")))

class DailyKos(forecast.Forecast):
    def __init__(self):
        self.lookup = False

    def load_lookup(self):
        if not self.lookup: 
            self.lookup = get_data("assign_tables_2016.js")["data"]

    def race_id_to_state(self, race_id):
        office_id = str(self.lookup["races"][str(race_id)]["office_id"])
        office = self.lookup["offices"][office_id]
        jurisdiction_id = str(office["jurisdiction_id"])
        jurisdiction = self.lookup["jurisdictions"][jurisdiction_id]
        abbr = jurisdiction["state_abbreviation"]
        return abbr

    def process_history(self, data, office):
        arr = []
        for race_id, projections in data.items():
            state = self.race_id_to_state(race_id)
            office_id = str(self.lookup["races"][str(race_id)]["office_id"])

            for proj in projections:
                for party in [ "democrat", "republican", "independent" ]:
                    if party not in proj["projection"]:
                        continue
                    win_prob = proj["projection"][party]
                    if party == "independent" and win_prob == 0:
                        continue # Ignore independents with 0 odds of winning
                    party_init = party[0].upper()
                    party_id = { "D": 1, "R": 2, }.get(party_init)
                    date = forecast.ts_to_date(proj["date"] / 1000)
                    if date > "2016-11-07": continue
                    if office == "P" and date >= "2016-08-05":
                        if state == "DC":
                            est_share = None
                        elif party_init == "D":
                            est_share = float(clinton_vote_shares[date][us.states.lookup(state).name])
                        elif party_init == "R":
                            est_share = 1 - float(clinton_vote_shares[date][us.states.lookup(state).name])
                        else:
                            est_share = None
                    else:
                        est_share = None
                    arr.append({
                        "date": date,
                        "model": "dailykos",
                        "office": office,
                        "party": party_init,
                        "state": state,
                        "candidate": PRES_CAND_DICT[party_init] if office == "P" else None,
                        "win_prob": win_prob,
                        "est_share_2p": est_share,
                        "est_share": None,
                        "est_diff": None
                    })
        return arr

    def process_latest(self, all_data):
        arr = []
        for office in [ "president", "senator" ]:
            data = all_data[office]["forecast"]["data"]
            date = data["date_created"]
            if date > "2016-11-07": continue
            for race_id, odds in data["state_win_probabilities"].items():
                state = self.race_id_to_state(race_id)
                for party in [ "democrat", "republican", "independent" ]:
                    if party not in odds:
                        continue
                    win_prob = odds[party]
                    if party == "independent" and win_prob == 0:
                        continue # Ignore independents with 0 odds of winning
                    party_init = party[0].upper()
                    office_init = office[0].upper()
                    if party in [ "democrat", "republican" ] and office == "president":
                        if state == "DC":
                            est_share = None
                        else:
                            est_share = data["state_vote_forecasts"][str(race_id)][party]["mid"]
                    else:
                        est_share = None
                    arr.append({
                        "date": date,
                        "model": "dailykos",
                        "office": office_init,
                        "party": party_init,
                        "state": state,
                        "candidate": PRES_CAND_DICT[party_init] if office_init == "P" else None,
                        "win_prob": win_prob,
                        "est_share_2p": est_share,
                        "est_share": None,
                        "est_diff": None,
                    })
        return arr

    def get_latest_predictions(self):
        self.load_lookup()
        data = get_data("assign_forecasts_2016.js")
        arr = self.process_latest(data)
        return forecast.Predictions(arr)

    def get_historical_predictions(self):
        self.load_lookup()
        president_data = get_data("presidential_state_forecast_history_2016.js")
        president = self.process_history(president_data, "P")
        senate_data = get_data("senate_state_forecast_history_2016.js")
        senate = self.process_history(senate_data, "S")
        latest = self.get_latest_predictions().prediction_list
        return forecast.Predictions(senate + president + latest)
