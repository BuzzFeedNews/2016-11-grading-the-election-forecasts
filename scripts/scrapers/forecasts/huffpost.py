import requests
from . import forecast
import datetime
import tarfile
import io
import csv
import re
import sys

BASE_URL = "http://elections.huffingtonpost.com/2016/forecast/"

PRES_CAND_DICT = {
    "D": "CLINTON",
    "R": "TRUMP",
}

def process_state(state, office):
    arr = []
    return arr

class HuffingtonPost(forecast.Forecast):
    def get_latest_predictions_senate(self):
        arr = []
        date = forecast.today_eastern()
        html = requests.get(BASE_URL + "senate")\
            .content.decode("utf-8")
        pat = r'(senate-curves[^"]+)'
        path = re.search(pat, html).group(1)
        raw = requests.get(BASE_URL + path)\
            .content.decode("utf-8")
        rows = csv.DictReader(
            io.StringIO(raw),
            delimiter="\t"
        )
        for row in rows:
            if row["date"] != "2016-11-08": continue
            dem_prob = float(row["dem_win_prob_with_undecided"])
            has_diff = row["diff_xibar"] != ""
            dem_diff = float(row["diff_xibar"]) if has_diff else None
            for party in [ "D", "R" ]:
                arr.append({
                    "date": date,
                    "model": "huffpost",
                    "office": "S",
                    "party": party,
                    "state": row["state"],
                    "candidate": None,
                    "win_prob": dem_prob if party == "D" else (1 - dem_prob),
                    "est_diff": (dem_diff if party == "D" else -dem_diff) if has_diff else None,
                    "est_share": None,
                    "est_share_2p": None,
                })
        return forecast.Predictions(arr)

    def get_latest_predictions_president(self):
        arr = []
        date = forecast.today_eastern()
        html = requests.get(BASE_URL + "president")\
            .content.decode("utf-8")
        pat = r'(president-summaries[^"]+)'
        path = re.search(pat, html).group(1)
        raw = requests.get(BASE_URL + path)\
            .content.decode("utf-8")
        rows = csv.DictReader(
            io.StringIO(raw),
            delimiter="\t"
        )
        for row in rows:
            dem_prob = float(row["clinton_win_prob"])
            dem_diff = float(row["diff_xibar"]) / 100
            for party in [ "D", "R" ]:
                arr.append({
                    "date": date,
                    "model": "huffpost",
                    "office": "P",
                    "party": party,
                    "state": row["state"],
                    "candidate": PRES_CAND_DICT[party],
                    "win_prob": dem_prob if party == "D" else (1 - dem_prob),
                    "est_diff": dem_diff if party == "D" else -dem_diff,
                    "est_share": None,
                    "est_share_2p": None,
                })
        return forecast.Predictions(arr)

    def get_latest_predictions(self):
        senate = self.get_latest_predictions_senate()
        president = self.get_latest_predictions_president()
        return forecast.Predictions(
            senate.prediction_list + president.prediction_list
        )
