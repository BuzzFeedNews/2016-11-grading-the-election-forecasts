default:

.PHONY: now
now:
	@date

data/forecasts/original/%.csv: now
	python -m scripts.scrapers.cli $* > $@

data/forecasts/combined.csv: now
	python scripts/combine-forecasts.py > $@
