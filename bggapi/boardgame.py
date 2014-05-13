from datetime import timedelta

from bggapi._internals import cached_property, HtmlStripper


class BoardGame(object):
    def __init__(self, boardgame):
        self._boardgame = boardgame

    @classmethod
    def by_id(cls, bgg_id):
        from bggapi.api import _fetch

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
    def age(self):
        age = self._find("age")
        return int(age) if age else None

    @cached_property
    def year(self):
        year = self._find("yearpublished")
        return int(year) if year else None

    @cached_property
    def mechanics(self):
        bgmechanics = []
        for bgmechanic in self._boardgame.findall("./boardgamemechanic"):
            bgmechanics.append(bgmechanic.text)
        return sorted(bgmechanics)

    @cached_property
    def categories(self):
        bgcategories = []
        for bgcategory in self._boardgame.findall("./boardgamecategory"):
            bgcategories.append(bgcategory.text)
        return sorted(bgcategories)

    @cached_property
    def rating(self):
        rating = self._find("statistics/ratings/average")
        return float(rating) if rating else None

    @cached_property
    def ranks(self):
        bgranks = {}
        for bgrank in self._boardgame.findall(
                "./statistics/ratings/ranks/rank"):
            bgranks[bgrank.attrib['name']] = int(bgrank.attrib['value'])
        return bgranks
