import re
import urllib2

from BeautifulSoup import BeautifulSoup

CHARTSHOW_URL = "http://www.thecurrent.org/feature/{year}/{month}/{day}/chart-show"


def get_chartshow_html(year, month, day):
    """Get the HTML for the given year, month day."""
    u = CHARTSHOW_URL.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2))
    return urllib2.urlopen(u, timeout=60).read()


def get_chartshow(html, year, month, day):
    """Parse through the HTML of chartshow to get weekly rankings."""
    soup = BeautifulSoup(html)
    results = ""

    if len(soup.findAll("table", {"class": "chartshow"})) > 0:
        for l in soup.findAll("table", {"class": "chartshow"})[0].findAll("tr")[2:]:
            cells = l.findAll("td")
            results = results + ",".join([cells[0].contents[0], cells[3].contents[0], cells[4].contents[0]]) + "\n"
    else:
        for p in soup.findAll('p'):
            if len(p.contents) == 41:
                for el in p:
                    if el is not None and len(el) > 0 and re.match("^[0-9].*$", el):
                        results = results + el.strip() + "\n"
    return results


def get_chartshow_csv(data):
    """Parse the raw data into CSV."""
    results = ""
    rank = 1
    for line in data.split("\n"):
        if len(line.strip()) > 0:
            if len(line.split(",")) == 3:
                results = results + line + "\n"
            else:
                m = re.match("^([0-9X]+)(.*)", line)
                n = re.search("[a-z][A-Z]", m.group(2))
                artist_song = m.group(2) + ","
                if n is not None:
                    index = line.find(n.group(0)) + 1
                    artist_song = line[:index].replace(m.group(1), "") + "," + line[index:]

                results = results + str(rank) + "," + artist_song + "\n"
                rank = rank + 1
    return results

