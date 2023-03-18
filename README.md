# The Current

Attempt to predict which musical artist will be played on Thursdays on 89.3 The Current (http://thecurrent.org).

## Setup

Create a Python virtual environment and install dependencies

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## The Basics

The Current posts their playlist by hour or by day to https://www.thecurrent.org/playlist/the-current/2021-01-01. 

The code is broken into two major compontents:

- __playlist.py__ - Retrieves HTML and parses the song information from https://www.thecurrent.org/playlist/the-current/. 
- __pipeline.py__ - The pipeline which orchestrates HTML retrieval using __playlist.py__ and generation of the CSV files.


A simple example of usage. The following code will retrieve the songs played for a specific hour.

```python
import playlist
playlist.get_hour(2016, 1, 24, 0)
```

## Running the pipeline

In order to prevent DoS'ing The Current website, a Luigi-based pipeline exists which downloads the HTML for a given day, parses the HTML for the articles, and save the results off as a CSV.

The following command will retrieve the HTML, save it to the `output/html` directory, parse the HTML for articles, and save the results as a CSV in the `output/csv` directory. Execute the pipeline like song

### Saving the HTML
Retrieve and save a single __hour__ HTML
```bash
export PYTHONPATH=.
luigi --module html_tasks SaveHourHtmlToLocal --date=2016-01-01 --hour=0 --local-scheduler
```

Retrieve and save a full day of HTML by __hour__ (24 hours)
```bash
export PYTHONPATH=.
luigi --module html_tasks SaveHourHtmlToLocal --date=2016-01-01 --local-scheduler
```

Hourly can be...alot. This allows retrieval for a full __day__
```bash
export PYTHONPATH=.
luigi --module html_tasks SaveDayHtmlToLocal --date=2016-01-01 --local-scheduler
```

Retrieve and save an entire __month__ of HTML
```bash
export PYTHONPATH=.
luigi --module html_tasks SaveMonthHtmlToLocal --year=2016 --month=1  --local-scheduler
```

Retrieve and save an entire __year__ of HTML
```bash
export PYTHONPATH=.
luigi --module html_tasks SaveYearHtmlToLocal --year=2016 --local-scheduler
```

## Generating CSVs
CSV generation requires the HTML has been saved down. If the HTML hasn't been retrieved yet the CSV task will retrieve the HTML and then create the file(s).

Convert a single day's HTML into the song CSV
```bash
export PYTHONPATH=.
luigi --module --module csv_tasks ConvertDayHtmlToCsv --year=2016 --local-scheduler --workers=10
```

## Song Dataset Fields

| field       | Type     | Description                                                   |
|-------------|----------|---------------------------------------------------------------|
| id          | string   | A unique identifier of the hashed datetime, artist, and title |
| datetime    | datetime | The time the song was played at                               |
| artist      | string   | The name of the artist who played the song                    |
| title       | string   | The title of the song                                         |
| year        | integer  | The year the song was played on the Current                   |
| month       | integer  | The month the song was played on the Current                  |
| day         | integer  | The day the song was played on the Current                    |
| day_of_week | string   | The friendly name of the day of week the song was played      |
| week        | integer  | The week of the year the song was played                      |
| hour        | integer  | The hour block the song was played (0-23)                     |

## Running the analysis

 1. Download Spark 2.0.1 from here: http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
 1. Untar it to the location /opt/spark-2.1.0-bin-hadoop2.7
 1. From the command line execute: source profile && pyspark

