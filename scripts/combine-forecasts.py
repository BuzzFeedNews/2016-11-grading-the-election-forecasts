#!/usr/bin/env python
import pandas as pd
import sys
import glob

# ## Load data
paths = glob.glob("data/forecasts/original/*.csv")
forecasts = pd.concat(list(map(pd.read_csv, paths)))
COL_ORDER = [ "date", "model", "office", "state", "party", "candidate", "win_prob", "est_diff", "est_share", "est_share_2p" ]
TIDY_COLS = [ "date", "office", "state", "party", "candidate", "model" ]
# ## Select only core, similarly-handled races
# 
# Ignore those on which the forecasts report differently. In the presidential election, ignore Maine's first and second districts and Nebraska's first, second, and third districts. In the Senate, ignore California and Louisiana.

PRES_IGNORE = [ "ME1", "ME2", "NE1", "NE2", "NE3",  ]
SEN_IGNORE = [ "CA", "CA2", "LA" ]

core_forecasts = forecasts[
    ~((forecasts["office"] == "P") & (forecasts["state"].isin(PRES_IGNORE))) &
    ~((forecasts["office"] == "S") & (forecasts["state"].isin(SEN_IGNORE))) &
    ~(forecasts["model"] == "538_now")
].copy().reset_index(drop=True)

# ## Fill in missing candidates
# 
# In Utah, for example, assign 0% odds to McMullin for forecasts that haven't published odds on him.

# Use New York Times's candidate names, for consistency's sake
core_forecasts["candidate"] = pd.merge(
    core_forecasts[TIDY_COLS[:-2]],
    core_forecasts[core_forecasts["model"] == "nyt"][[
        "office", "state", "party", "candidate"
    ]].drop_duplicates(),
    on=TIDY_COLS[1:-2],
    how="left"
)["candidate"]

# Add in the few missing candidates
core_forecasts.loc[(
    (core_forecasts["party"] == "L") &
    (core_forecasts["office"] == "P")
), "candidate"] = "JOHNSON"
core_forecasts.loc[(
    (core_forecasts["state"] == "NC") &
    (core_forecasts["party"] == "L") &
    (core_forecasts["office"] == "S")
), "candidate"] = "HAUGH"

def normalize_rounded_probs(df):
    df["win_prob"] = df["win_prob"] / df["win_prob"].sum()
    return df

core_forecasts = core_forecasts.groupby([
    "date", "model", "office", "state"
]).apply(normalize_rounded_probs)

# Fill in PEC and PredictWise-market's "safe" Senate seats
def get_implicit_predictions(forecasts, forecast_name):
    fc = forecasts[
        forecasts["model"] == forecast_name
    ]
    fc_ids = fc[[ "date", "office", "state" ]].astype(str)\
        .apply("|".join, axis=1)
    favorites = forecasts.groupby(TIDY_COLS[:-1])["win_prob"].mean().round()\
        .reset_index()
    favorites_ids = favorites[[ "date", "office", "state" ]].astype(str)\
        .apply("|".join, axis=1)
    implicit = favorites[
        favorites["date"].isin(fc["date"].unique()) &
        ~favorites_ids.isin(fc_ids)
    ].copy()   
    implicit["model"] = forecast_name
    return implicit

pec_implicit = get_implicit_predictions(core_forecasts, "pec")
pwm_implicit = get_implicit_predictions(core_forecasts, "predictwise_markets")
# Make sure that we haven't included any 50/50 races, which would round to a total probability of 2
def test_implicit_for_splits(implicit):
    assert(implicit.groupby(["date", "office", "state"])["win_prob"].sum().unique() == [1])
test_implicit_for_splits(pec_implicit)
test_implicit_for_splits(pwm_implicit)
core_forecasts = pd.concat([
    core_forecasts,
    pec_implicit,
    pwm_implicit
]).reset_index(drop=True)

core_forecasts["opp_party"] = core_forecasts["party"].apply({ "D": "R", "R": "D" }.get)
opps = pd.merge(
    core_forecasts,
    core_forecasts[[ "date", "model", "office", "state", "party", "est_share" ]],
    left_on=[ "date", "model", "office", "state", "opp_party" ],
    right_on=[ "date", "model", "office", "state", "party" ],
    how="left",
    suffixes=[".self", ".opp"]
)
core_forecasts["est_diff"] = core_forecasts["est_diff"].fillna(
    opps["est_share.self"] - opps["est_share.opp"]
)
core_forecasts["est_share_2p"] = core_forecasts["est_share_2p"].fillna(
    opps["est_share.self"] / (opps["est_share.self"] + opps["est_share.opp"])
)

# Make sure we pass basic tests
assert(core_forecasts["model"].nunique() == 11)
assert(core_forecasts.groupby(TIDY_COLS).size().value_counts().index == [ 1 ])

# Remove floating point cruft
core_forecasts["win_prob"] = core_forecasts["win_prob"].apply("{0:.5f}".format)
core_forecasts.loc[core_forecasts["est_diff"].notnull(), "est_diff"] = core_forecasts["est_diff"].apply("{0:.5f}".format)
core_forecasts.loc[core_forecasts["est_share"].notnull(), "est_share"] = core_forecasts["est_share"].apply("{0:.5f}".format)
core_forecasts.loc[core_forecasts["est_share_2p"].notnull(), "est_share_2p"] = core_forecasts["est_share_2p"].apply("{0:.5f}".format)

core_forecasts[COL_ORDER].sort_values(COL_ORDER).to_csv(sys.stdout, index=False)
