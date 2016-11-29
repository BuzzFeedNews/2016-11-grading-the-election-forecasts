import requests
from . import forecast
import datetime
import itertools
from operator import itemgetter
import tarfile
import io
import csv
import re
import sys, os

BASE_URL = "http://election.princeton.edu/code/data_archive/"
MIN_DAY = 187
MAX_DAY = 312

PRES_CAND_DICT = {
    "D": "CLINTON",
    "R": "TRUMP",
}

CUSTOM_STATES = {
    "M1": "ME1",
    "M2": "ME2",
    "N1": "NE1",
    "N2": "NE2",
    "N3": "NE3",
}

PRES_STATES = "AL AK AZ AR CA CO CT DC DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split(" ")
SEN_STATES = "AK AZ CO FL IA IL IN LA MO NC NH NV OH PA WI".split(" ")

STATE_ORDERS = {
    "P": dict((st, i) for i, st in enumerate(PRES_STATES)),
    "S": dict((st, i) for i, st in enumerate(SEN_STATES))
}


class PEC(forecast.Forecast):
    def __init__(self):
        self.load_diffs()

    def read_csv(self, string):
        return [ re.split(r" +", row.strip().replace(",", " "))
            for row in string.strip().split("\n") ]

    def read_csv_from_tar(self, t, name):
        string = t.extractfile(name).read().decode("latin-1")
        return self.read_csv(string)

    def load_diffs(self):
        DATA_DIR = "http://election.princeton.edu/code/data/"
        pres_csv = self.read_csv(requests.get(DATA_DIR + "2016.EV.polls.median.txt").content.decode("latin-1"))
        sen_csv = self.read_csv(requests.get(DATA_DIR + "2016.Senate.polls.median.txt").content.decode("latin-1"))
        self.diffs = {
            "P": dict((x, list(y)) for x, y in itertools.groupby(pres_csv, itemgetter(-2))),
            "S": dict((x, list(y)) for x, y in itertools.groupby(sen_csv, itemgetter(-2)))
        }

    def fetch_archive(self, num, use_cache=True):
        cache_path = "pec-cache/{0}.tgz".format(num)
        if use_cache and os.path.isfile(cache_path):
            fileobj = open(cache_path, "rb")
        else:
            url = BASE_URL + str(num) + ".tgz"
            c = requests.get(url).content
            if use_cache and os.path.isdir("pec-cache"):
                with open(cache_path, "wb") as f:
                    f.write(c) 
            fileobj = io.BytesIO(c)
        t = tarfile.open(fileobj=fileobj)
        return t

    def process_office(self, num, prob_rows, office, date):
        arr = []
        for state in prob_rows:
            state_raw = state[4 if office == "P" else 5]
            state_abbr = CUSTOM_STATES.get(state_raw, state_raw)
            if state_abbr in CUSTOM_STATES.values():
                dem_diff = None
            else:
                diffs = self.diffs[office][str(num)]
                diff_row = diffs[STATE_ORDERS[office][state_abbr]]
                dem_diff = float(diff_row[2]) / 100
            prob_col = -1 if office == "P" else 1
            dem_prob = float(state[prob_col]) / 100
            for party in [ "D", "R" ]:
                arr.append({
                    "date": date,
                    "model": "pec",
                    "office": office,
                    "party": party,
                    "state": state_abbr,
                    "candidate": PRES_CAND_DICT[party] if office == "P" else None,
                    "win_prob": dem_prob if party == "D" else (1 - dem_prob),
                    "est_diff": (dem_diff if party == "D" else -dem_diff) if dem_diff else None,
                    "est_share": None,
                    "est_share_2p": None,
                })
        return arr

    def parse_single_archive(self, num, tar):
        date = (
            datetime.date(2015, 12, 31) + datetime.timedelta(days=num)
        ).strftime("%Y-%m-%d")
        pres_probs = self.read_csv_from_tar(tar, "data/EV_stateprobs.csv")
        sen_probs = self.read_csv_from_tar(tar, "data/Senate_stateprobs.csv")
        pres_predictions = self.process_office(num, pres_probs, "P", date)
        sen_predictions = self.process_office(num, sen_probs, "S", date)
        return pres_predictions + sen_predictions

    def get_historical_predictions(self, starting_day=MIN_DAY):
        html = requests.get(BASE_URL).content.decode("latin-1")
        matches = re.findall(r"(\d+).tgz", html)
        max_day = min([ max(map(int, matches)), MAX_DAY ])
        arr = []
        for num in range(starting_day, max_day + 1):
            sys.stderr.write("{0}\n".format(num))
            tar = self.fetch_archive(num, use_cache=(num < max_day))
            arr += self.parse_single_archive(num, tar)
        return forecast.Predictions(arr)
