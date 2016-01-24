import urllib2

from BeautifulSoup import BeautifulSoup

url = "http://www.thecurrent.org/playlist/{year}-{month}-{day}/{hour}?isajax=1"


class Article(object):
    @property
    def id(self):
        return dict(self.node.attrs)["id"]

    @property
    def date(self):
        return dict(self.node.find("time").attrs)["datetime"]

    @property
    def time(self):
        return self.node.find("time").contents[0]

    @property
    def title(self):
        return self.node.find("h5", {"class": "title"}).contents[0].strip()

    @property
    def artist(self):
        return self.node.find("h5", {"class": "artist"}).contents[0].strip()

    def __init__(self, node):
        self.node = node


def get_hour(year, month, day, hour):
    u = url.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2), hour=hour)
    page = urllib2.urlopen(u).read()
    soup = BeautifulSoup(page)
    for node in soup.findAll("article"):
        a = Article(node)
        print a.artist

get_hour(2016, 1, 24, 0)
