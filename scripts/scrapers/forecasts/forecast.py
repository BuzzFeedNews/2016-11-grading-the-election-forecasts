import csv
import datetime
import dateparser
import pytz
from operator import itemgetter

PREDICTION_FIELDS = [
    "date",
    "model",
    "office",
    "state",
    "party",
    "candidate",
    "win_prob",
    "est_diff",
    "est_share",
    "est_share_2p",
]

EASTERN = pytz.timezone('US/Eastern')
DATE_FMT = "%Y-%m-%d"

def today_eastern():
    dt = datetime.datetime.now(tz=pytz.utc).astimezone(EASTERN)
    return dt.strftime(DATE_FMT)

def ts_to_date(ts):
    if isinstance(ts, (int, float)):
        d = datetime.datetime.fromtimestamp(ts, tz=pytz.utc).astimezone(EASTERN)
    else:
        d = dateparser.parse(ts).astimezone(EASTERN)
    return d.strftime(DATE_FMT)

class Predictions(object):
    def __init__(self, prediction_list):
        self.prediction_list = prediction_list

    def to_csv(self, dest):
        writer = csv.DictWriter(dest, fieldnames=PREDICTION_FIELDS)
        writer.writeheader()
        for p in sorted(self.prediction_list, key=itemgetter(*PREDICTION_FIELDS)):
            row = dict(p)
            row["win_prob"] = float("{0:5f}".format(row["win_prob"]))
            if row["est_diff"] != None:
                row["est_diff"] = float("{0:5f}".format(row["est_diff"]))
            if row["est_share"] != None:
                row["est_share"] = float("{0:5f}".format(row["est_share"]))
            if row["est_share_2p"] != None:
                row["est_share_2p"] = float("{0:5f}".format(row["est_share_2p"]))
            writer.writerow(row)

class Forecast(object):
    def get_latest_predictions(self):
        return False

    def get_historical_predictions(self):
        return False
