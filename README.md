# Grading The 2016 Election Forecasts

This repository contains data and code supporting BuzzFeed News' [evaluation of forecasters' predictions for the November 2016 U.S. presidential and Senate elections](https://www.buzzfeed.com/jsvine/2016-election-forecast-grades).

## Methodology

The methodology — published on afternoon of Election Day, before the polls closed — can be [found here](https://www.buzzfeed.com/jsvine/grading-the-2016-election-forecasts).

## Data

This repository contains data for the nine forecasters named in [the methodology](https://www.buzzfeed.com/jsvine/grading-the-2016-election-forecasts).

The [`data/forecasts/original`](data/forecasts/original) directory contains one file per forecaster, and draws only on data available directly from the forecasters' websites or provided by the forecasters to BuzzFeed News before the election. The Python scripts used to collect this data can be found in the [`scripts/scrapers`](scripts/scrapers/) directory.

The [`data/forecasts/combined.csv`](data/forecasts/combined.csv) file merges the files in `original` and does the following:

- Removes presidential forecasts for Maine and Nebraska's district-allocated electoral votes, as well as California and Louisiana's Senate races. (California’s Senate race pitted two Democrats against one another, while Louisiana's contest was technically a primary.)

- Adds implied probabilities for candidacies that the forecasters didn't explicitly score. (E.g., Evan McMullin or Gary Johnson in the presidential race, or extraordinarily "safe" Senate races.)

- Converts estimated vote shares to `Dem.-Rep.` vote share margins where available.

- Standardizes probabilities that, because of imprecision due to rounding, do not sum to 100.00%.

- Standardizes the candidates' names.

Both the `original/*.csv` and `combined.csv` files use the following structure, with one line per date-model-candidate combination:

- `date`:  The date of the forecast.
- `model`: The particular forecast model. In some cases forecasters produce multiple models, e.g., FiveThirtyEight's "polls-plus" and "polls-only" models.
- `office`: `P` for President, or `S` for Senate.
- `state` : The postal code corresponding to the state being forecasted.
- `party`: `R` for Republican, `D` for Democrat, `L` for Libertarian, and `I` for independent.
- `candidate`: The candidate's last name.
- `win_prob`: The probability assigned to that candidate winning. Ranges from 0 to 1.
- `est_diff`: For major-party candidates, the model's estimated difference between this candidate's and his/her opponent's proportions of the vote.
- `est_share`: The candidate's estimated share of the vote, overall.
- `est_share_2p`: The candidate's estimated share of the two-party vote — i.e., excluding third-party candidates.

#### A note on vote-shares and vote-share differences

Forecasters represented candidates' expected margin of victory in slightly different ways that can't all be converted into a single, perfectly-comparable metric. Ultimately, though, we can group the forecasts into two types:

- Forecasts that allow calculation of Trump’s expected __percentage-point margin of victory over Clinton__, among all votes. This group contains FiveThirtyEight, PollSavvy, the New York Times, the Princeton Election Consortium, and the Huffington Post.

- Forecasts that allow calculation of Trump’s expected __share of the two-party vote__ (i.e., excluding Johnson, Stein, and McMullin). This group contains FiveThirtyEight, PollSavvy, Daily Kos, Kremp/Slate, and Desart and Holbrook. (PredictWise did not make any vote-share projections.)

### Related data

- The Huffington Post has published its [data pipeline and full forecast history on GitHub](https://github.com/huffpostdata/predictions-2016).

## Results

A Jupyter notebook containing the forecast evaluations can be [found here](notebooks/forecast-analysis.ipynb).

## Feedback / Questions?

Contact Jeremy Singer-Vine at jeremy.singer-vine@buzzfeed.com.

Looking for more from BuzzFeed News? [Click here for a list of our open-sourced projects, data, and code](https://github.com/BuzzFeedNews/everything).
