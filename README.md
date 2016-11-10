# The Current Parser
A python script for parsing a given hour's playlist from http://thecurrent.org. The following code contains functions for scraping and piplining the processing of data for a given hour, day, or month. This makes it easy to quickly retrieve the data from The Current's website

## Setup
Create a Python virtual environment and install dependencies
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## The Basics
Each play of a song is considered an "article" by The Current. The Current posts their playlist by hour or by day.

The following code will retrieve a specific hour
```
import playlist
playlist.get_hour(2016, 1, 24, 0)
```

## Saving the data
In order to prevent DoS'ing The Current website, a Luigi-based pipeline exists which downloads the HTML for a given day, parses the HTML for the articles, and save the results off as a CSV.

The following command will retrieve the HTML, save it to the `output/html` directory, parse the HTML for articles, and save the results as a CSV in the `output/csv` directory. Execute the pipeline like song
```
export PYTHONPATH=.
luigi --module pipeline DayHtmlToArticlesCsv --date=2016-01-01 --local-scheduler
```
