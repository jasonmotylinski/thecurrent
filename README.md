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

The code is broken into the major components:

- __playlist.py__ - Retrieves HTML and parses the song information from https://www.thecurrent.org/playlist/the-current/. 
- __html_tasks.py__ - Tasks to orchestrates HTML retrieval using __playlist.py__ 
- __csv_tasks.py__ - Tasks to parse out data from HTML retrieved from __html_tasks.py__


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
luigi --module --module csv_tasks ConvertDayHtmlToCsv --date=2016-01-01 --local-scheduler --workers=10
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

## Running the Notebooks

In VSCode change the `Jupyter Notebook File Root` setting to 
```
${workspaceFolder}
```

## Backlog of stations to integrate

A list of popular independent and public radio stations in the AAA (Adult Album Alternative) format. These stations feature diverse playlists including indie rock, folk, singer-songwriter, Americana, world music, and alternative genres.

### Northeast
| Station | City | Website |
|---------|------|---------|
| WXRV (92.5 The River) | Boston, MA | https://www.river.com/ |
| WERS (88.9) | Boston, MA | https://wers.org/ |
| WUMB (91.9) | Boston, MA | https://wumb.org/ |
| WCLZ (98.9) | Portland, ME | https://989wclz.com/ |
| WEXT (97.7) | Albany, NY | https://www.wextradio.org/ |
| WMVY (92.7 MVY Radio) | Martha's Vineyard, MA | https://www.mvyradio.org/ |
| WRSI (93.9 The River) | Northampton, MA | https://www.wrsi.com/ |
| WDST (100.1 Radio Woodstock) | Woodstock, NY | https://wdst.com/ |
| WNCS (104.7 The Point) | Burlington, VT | https://www.pointfm.com/ |
| WXPK (107.1 The Peak) | Westchester, NY | https://www.1071thepeak.com/ |

### Mid-Atlantic
| Station | City | Website |
|---------|------|---------|
| WTMD (89.7) | Baltimore, MD | https://www.wtmd.org/ |
| WRNR (103.1) | Annapolis, MD | https://wrnr.com/ |
| WSGE (91.7) | Charlotte, NC | https://wsge.org/ |

### Southeast
| Station | City | Website |
|---------|------|---------|
| WFPK (91.9) | Louisville, KY | https://www.lpm.org/music |
| WRLT (100.1 Lightning 100) | Nashville, TN | https://lightning100.com/ |
| WMOT (89.5 Roots Radio) | Nashville, TN | https://www.wmot.org/ |
| WNCW (88.7) | Spindale, NC | https://www.wncw.org/ |
| WDVX (89.9) | Knoxville, TN | https://wdvx.com/ |
| WEVL (89.9) | Memphis, TN | https://www.wevl.org/ |
| WMNF (88.5) | Tampa, FL | https://www.wmnf.org/ |

### Midwest
| Station | City | Website |
|---------|------|---------|
| WXRT (93.1) | Chicago, IL | https://wxrt.radio.com/ |
| KFAI (90.3) | Minneapolis, MN | https://kfai.org/ |
| WCBE (90.5) | Columbus, OH | https://www.wcbe.org/ |
| WTTS (92.3) | Indianapolis, IN | https://www.wtts.com/ |
| WEMU (89.1) | Ann Arbor, MI | https://www.wemu.org/ |
| WDET (101.9) | Detroit, MI | https://wdet.org/ |
| WYCE (88.1) | Grand Rapids, MI | https://wyce.org/ |
| WOJB (88.9) | Hayward, WI | https://wojb.org/ |
| KTBG (90.9 The Bridge) | Kansas City, MO | https://bridge909.org/ |
| KDHX (88.1) | St. Louis, MO | https://kdhx.org/ |

### Southwest
| Station | City | Website |
|---------|------|---------|
| KGSR (93.3) | Austin, TX | https://www.kgsr.com/ |
| KHYI (95.3 The Range) | Dallas, TX | https://khyi.com/ |
| KBAC (98.1 Radio Free Santa Fe) | Santa Fe, NM | https://kbac.com/ |
| KXCI (91.3) | Tucson, AZ | https://kxci.org/ |
| KANW (89.1) | Albuquerque, NM | https://www.kanw.com/ |
| KUVO (89.3) | Denver, CO | https://www.kuvo.org/ |

### Mountain
| Station | City | Website |
|---------|------|---------|
| KBCO (97.3) | Denver, CO | https://kbco.iheart.com/ |
| KVOQ (99.9) | Denver, CO | https://www.cpr.org/ |
| KSPN (91.1) | Aspen, CO | https://www.aspenpublicradio.org/ |
| KRCL (90.9) | Salt Lake City, UT | https://krcl.org/ |
| KZMU (90.1) | Moab, UT | https://www.kzmu.org/ |

### Pacific Northwest
| Station | City | Website |
|---------|------|---------|
| KINK (101.9) | Portland, OR | https://kink.fm/ |
| KNKX (88.5) | Seattle/Tacoma, WA | https://www.knkx.org/ |
| KAOS (89.3) | Olympia, WA | https://kaosradio.org/ |
| KBCS (91.3) | Bellevue, WA | https://kbcs.fm/ |

### California
| Station | City | Website |
|---------|------|---------|
| KCSN (88.5 The SoCal Sound) | Los Angeles, CA | https://kcsn.org/ |
| KPIG (107.5) | Freedom, CA | https://kpig.com/ |
| KHUM (104.3/104.7) | Humboldt County, CA | https://www.khum.com/ |
| KRSH (95.9 The Krush) | Santa Rosa, CA | https://krsh.com/ |

### South & Central
| Station | City | Website |
|---------|------|---------|
| KUAF (91.3) | Fayetteville, AR | https://www.kuaf.com/ |
| KOSU (91.7) | Stillwater, OK | https://kosu.org/ |
| KRVS (88.7 Radio Acadie) | Lafayette, LA | https://www.krvs.org/ |

### Canada
| Station | City | Website |
|---------|------|---------|
| CFRO (100.5 Co-op Radio) | Vancouver, BC | https://www.coopradio.org/ |
| CKUW (95.9) | Winnipeg, MB | https://ckuw.ca/ |

---

**Currently Integrated (11 stations):**
- KCMP (89.3 The Current) - Minneapolis
- KEXP - Seattle
- KUTX - Austin
- WXPN - Philadelphia
- WFUV - New York
- KCRW - Los Angeles
- KUOM (Radio K) - Minneapolis
- KKXT (KXT) - Dallas
- WEHM - Long Island
- WNXP - Nashville
- WYEP - Pittsburgh