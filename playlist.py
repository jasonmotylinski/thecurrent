import md5
import urllib2
import unicodedata

from datetime import datetime
from BeautifulSoup import BeautifulSoup
from pytz import timezone

HOUR_URL = "http://www.thecurrent.org/playlist/{year}-{month}-{day}/{hour}"
DAY_URL = "http://www.thecurrent.org/playlist/{year}-{month}-{day}/"

HOUR_MAP = {
    "11:00 pm to 12:00 am": 23,
    "10:00 pm to 11:00 pm": 22,
    "9:00 pm to 10:00 pm":  21,
    "8:00 pm to  9:00 pm":   20,
    "7:00 pm to  8:00 pm":   19,
    "6:00 pm to  7:00 pm":   18,
    "5:00 pm to  6:00 pm":   17,
    "4:00 pm to  5:00 pm":   16,
    "3:00 pm to  4:00 pm":   15,
    "2:00 pm to  3:00 pm":   14,
    "1:00 pm to  2:00 pm":   13,
    "12:00 pm to  1:00 pm":  12,
    "11:00 am to 12:00 pm": 11,
    "10:00 am to 11:00 am": 10,
    "9:00 am to 10:00 am":  9,
    "8:00 am to  9:00 am":   8,
    "7:00 am to  8:00 am":   7,
    "6:00 am to  7:00 am":   6,
    "5:00 am to  6:00 am":   5,
    "4:00 am to  5:00 am":   4,
    "3:00 am to  4:00 am":   3,
    "2:00 am to  3:00 am":   2,
    "1:00 am to  2:00 am":   1,
    "1:00 am to  3:00 am":   1,
    "12:00 am to  1:00 am":  0
}


class Article(object):
    """An article, which represents a play."""

    @property
    def id(self):
        """Generate the id of the article."""
        m = md5.new()
        m.update("{0}{1}{2}".format(self.datetime, unicodedata.normalize('NFKD', self.artist).encode('ascii','ignore'), unicodedata.normalize('NFKD', self.title).encode('ascii','ignore')))
        return m.hexdigest()

    @property
    def date(self):
        """Parse the date of the article."""
        return self._date

    @property
    def time(self):
        """Parse the time of the article."""
        return self.node.find("time").contents[0].strip()

    @property
    def datetime(self):
        """Parse the date and time of the article."""
        am_pm = "AM"
        if self._date.hour > 11:
            am_pm = "PM"
        d = datetime.strptime(self.date.strftime("%Y%m%d") + " " + self.time + " " + am_pm, "%Y%m%d %I:%M %p")
        d.replace(tzinfo=timezone('US/Central'))
        return d


    @property
    def title(self):
        """Parse the title of the article."""
        return self.node.find("h5", {"class": "title"}).contents[0].strip()

    @property
    def artist(self):
        """Parse the artist of the article."""
        return self.node.find("h5", {"class": "artist"}).contents[0].strip()

    def __init__(self, node, date):
        """Constructor. Sets the node of the article retrieved from the HTML."""
        self.node = node
        self._date = date


def get_hour(year, month, day, hour):
    """Get the articles for a given year, month, day, hour."""
    u = HOUR_URL.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2), hour=hour)
    page = urllib2.urlopen(u, timeout=60).read()
    soup = BeautifulSoup(page)
    for node in soup.findAll("article", {"class": "row song"}):
        yield Article(node, datetime(year, month, day, int(hour)))


def get_day(year, month, day):
    """Get the articles for a given year, month, day, hour."""
    yield get_articles(get_day_html(year, month, day), year, month, day)


def get_day_html(year, month, day):
    """Get the HTML for the given day."""
    u = DAY_URL.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2))
    return urllib2.urlopen(u, timeout=60).read()


def get_articles(html, year, month, day):
    soup = BeautifulSoup(html)
    for node in soup.findAll("article", {"class": "row song"}):
        hour_node = node.findPreviousSibling("div", {"class": "hour"})
        hour_str = hour_node.find("span", {"class": "hour-header open"}).contents[0].strip()
        yield Article(node, datetime(year, month, day, HOUR_MAP[hour_str]))
