import sys
from .forecasts import (
    dailykos,
    desart,
    fivethirtyeight,
    huffpost,
    nyt,
    pec,
    predictwise,
    kremp,
    pollsavvy,
)

SCRAPERS = {
    "538": fivethirtyeight.FiveThirtyEight,
    "dailykos": dailykos.DailyKos,
    "desart": desart.DeSartAndHolbrook,
    "huffpost": huffpost.HuffingtonPost,
    "nyt": nyt.NYT,
    "pec": pec.PEC,
    "predictwise": predictwise.PredictWise,
    "kremp": kremp.Kremp,
    "pollsavvy": pollsavvy.PollSavvy,
}

scraper = SCRAPERS[sys.argv[1]]()
predictions = scraper.get_historical_predictions()
if not predictions:
    predictions = scraper.get_latest_predictions()
predictions.to_csv(sys.stdout)
