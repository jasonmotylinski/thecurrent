# The Current
Attempt to predict which musical artist wil be played on Thursdays on 89.3 The Current (http://thecurrent.org).
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

## Saving the source data
In order to prevent DoS'ing The Current website, a Luigi-based pipeline exists which downloads the HTML for a given day, parses the HTML for the articles, and save the results off as a CSV.

The following command will retrieve the HTML, save it to the `output/html` directory, parse the HTML for articles, and save the results as a CSV in the `output/csv` directory. Execute the pipeline like song
```
export PYTHONPATH=.
luigi --module pipeline DayHtmlToArticlesCsv --date=2016-01-01 --local-scheduler
```

To save an entire year's worth of playlist to CSV:
```
export PYTHONPATH=.
luigi --module pipeline CombineYearArticlesCsv --year=2016 --local-scheduler --workers=10
```

## Running the analysis
 1. Download Spark 2.0.1 from here: http://d3kbcqa49mib13.cloudfront.net/spark-2.0.1-bin-hadoop2.7.tgz
 1. Untar it to the location /opt/spark-2.0.1-bin-hadoop2.7
 1. From the command line execute: source profile && pyspark

