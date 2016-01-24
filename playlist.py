import urllib2

from BeautifulSoup import BeautifulSoup

url = "http://www.thecurrent.org/playlist/{year}-{month}-{day}/{hour}?isajax=1"


def get_hour(year, month, day, hour):
    u = url.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2), hour=hour)
    page = urllib2.urlopen(u).read()
    soup = BeautifulSoup(page)
    print soup.prettify()

get_hour(2016, 1, 24, 0)
