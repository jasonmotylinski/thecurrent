"""Parses the playlist for a given hour for http://thecurrent.org."""
import urllib2

from BeautifulSoup import BeautifulSoup

url = "http://www.thecurrent.org/playlist/{year}-{month}-{day}/{hour}?isajax=1"


class Article(object):
    """An article, which represents a play."""

    @property
    def id(self):
        """Parse the id of the article."""
        return dict(self.node.attrs)["id"]

    @property
    def date(self):
        """Parse the date of the article."""
        return dict(self.node.find("time").attrs)["datetime"]

    @property
    def time(self):
        """Parse the time of the article."""
        return self.node.find("time").contents[0]

    @property
    def title(self):
        """Parse the title of the article."""
        return self.node.find("h5", {"class": "title"}).contents[0].strip()

    @property
    def artist(self):
        """Parse the artist of the article."""
        return self.node.find("h5", {"class": "artist"}).contents[0].strip()

    def __init__(self, node):
        """Constructor. Sets the node of the article retrieved from the HTML."""
        self.node = node


def get_hour(year, month, day, hour):
    """Get the articles for a given year, month, day, hour."""
    u = url.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2), hour=hour)
    page = urllib2.urlopen(u).read()
    soup = BeautifulSoup(page)
    for node in soup.findAll("article", {"class": "row song"}):
        yield Article(node)
