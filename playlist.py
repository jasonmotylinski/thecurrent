import md5
import urllib2

from BeautifulSoup import BeautifulSoup
from datetime import datetime

url = "http://www.thecurrent.org/playlist/{year}-{month}-{day}/{hour}?isajax=1"


class Article(object):
    """An article, which represents a play."""

    @property
    def id(self):
        """Generate the id of the article."""
        m = md5.new()
        m.update("{0}{1}{2}".format(self.datetime, self.artist, self.title))
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
        return datetime.strptime(self.date.strftime("%Y%m%d") + " " + self.time, "%Y%m%d %I:%M")

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
    u = url.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2), hour=hour)
    page = urllib2.urlopen(u).read()
    soup = BeautifulSoup(page)
    for node in soup.findAll("article", {"class": "row song"}):
        yield Article(node, datetime(year, month, day))
