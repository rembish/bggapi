from datetime import timedelta
from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser
from urllib import quote
from urllib2 import urlopen
from xml.etree.cElementTree import parse


__all__ = ['BoardGame', 'search']
BASE_URL = 'http://www.boardgamegeek.com/xmlapi'


class _Missing(object):
    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()


class CachedProperty(object):
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value

        return value

cached_property = CachedProperty


class HtmlStripper(HTMLParser, object):
    def __init__(self):
        super(HtmlStripper, self).__init__()

        self.reset()
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        codepoint = int(number[1:], 16) \
            if number[0] in (u'x', u'X') else int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        codepoint = name2codepoint[name]
        self.result.append(unichr(codepoint))

    def handle_startendtag(self, tag, attrs):
        if tag.lower() == "br":
            self.result.append("\n")

    handle_starttag = handle_startendtag

    def get_data(self):
        return ''.join(self.result)


class BoardGame(object):
    def __init__(self, boardgame):
        self._boardgame = boardgame

    @classmethod
    def by_id(cls, bgg_id):
        for boardgame in _fetch([bgg_id]):
            return boardgame

        raise IOError("Unknown BGG id: %s" % bgg_id)

    def __repr__(self):
        return '<%s[%d] %s>' % (self.__class__.__name__, self.id, self.title)

    def __str__(self):
        return self.title

    def _find(self, tag):
        element = self._boardgame.find('./%s' % tag)
        return element.text if element is not None else None

    @cached_property
    def id(self):
        return int(self._boardgame.attrib['objectid'])

    @cached_property
    def title(self):
        title = self._find('name[@primary="true"]')
        return title.encode('utf-8') if title else None

    @cached_property
    def aliases(self):
        titles = []
        for name in self._boardgame.findall("./name"):
            if name is not None:
                title = name.text.encode("utf-8")
                if title != self.title:
                    titles.append(title)

        return titles

    @cached_property
    def thumbnail_url(self):
        return self._find("thumbnail")

    @cached_property
    def image_url(self):
        return self._find("image")

    @cached_property
    def url(self):
        return 'http://boardgamegeek.com/boardgame/%d' % self.id

    @cached_property
    def description(self):
        description = self._find("description").encode("utf-8")

        if description:
            striper = HtmlStripper()
            striper.feed(description)
            return striper.get_data()

    @cached_property
    def playing_time(self):
        minutes = self._find("playingtime")
        return timedelta(minutes=int(minutes)) if minutes else None

    @cached_property
    def min_players(self):
        players = self._find("minplayers")
        return int(players) if players else None

    @cached_property
    def max_players(self):
        players = self._find("maxplayers")
        return int(players) if players else None

    @cached_property
    def year(self):
        year = self._find("yearpublished")
        return int(year) if year else None

    @cached_property
    def rating(self):
        rating = self._find("statistics/ratings/average")
        return float(rating) if rating else None


def search(title, exact=False):
    url = '%s/search?search=%s&exact=%d' % (
        BASE_URL, quote(str(title)), 1 if exact else 0)

    root = parse(urlopen(url)).getroot()
    ids = map(lambda game: game.attrib['objectid'], root.iter("boardgame"))
    return _fetch(ids) if ids else []


def _fetch(ids):
    url = '%s/boardgame/%s?stats=1' % (BASE_URL, ','.join(map(str, ids)))
    root = parse(urlopen(url)).getroot()

    games = []
    for boardgame in root.iter("boardgame"):
        if 'objectid' not in boardgame.attrib:
            continue

        game = BoardGame(boardgame)
        games.append(game)

    return sorted(games, key=lambda x: x.id)
