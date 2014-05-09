from urllib import quote
from urllib2 import urlopen
from xml.etree.cElementTree import parse


class BoardGame(object):
    def __init__(self, bgg_id, title, **kwargs):
        self.id = bgg_id
        self.title = title

        self.attributes = kwargs

    def __repr__(self):
        return '<%s[%d] %s>' % (self.__class__.__name__, self.id, self.title)

    def __getattr__(self, item):
        if item in self.attributes:
            return self.attributes[item]
        raise AttributeError(item)


class BGGApi(object):
    base = 'http://www.boardgamegeek.com/xmlapi'

    def search(self, title, exact=False):
        url = '%s/search?search=%s&exact=%d' % (
            self.base, quote(str(title)), 1 if exact else 0
        )

        root = parse(urlopen(url)).getroot()

        ids = []
        for boardgame in root.iter("boardgame"):
            ids.append(boardgame.attrib['objectid'])

        return self._fetch(ids) if ids else []

    def get(self, bgg_id):
        for boardgame in self._fetch([bgg_id]):
            return boardgame

    def _fetch(self, ids):
        url = '%s/boardgame/%s' % (self.base, ','.join(map(str, ids)))
        root = parse(urlopen(url)).getroot()

        for boardgame in root.iter("boardgame"):
            if 'objectid' not in boardgame.attrib:
                continue

            id = int(boardgame.attrib['objectid'])
            year = int(boardgame.find('./yearpublished').text)
            title = boardgame.find('./name[@primary="true"]').text
            aliases = map(lambda x: x.text, boardgame.findall('./name'))
            players = [
                int(boardgame.find('./minplayers').text),
                int(boardgame.find('./maxplayers').text)
            ]
            playtime = int(boardgame.find('./playingtime').text)
            description = boardgame.find('./description').text
            thumbnail = boardgame.find('./thumbnail').text
            image = boardgame.find('./image').text

            game = BoardGame(
                bgg_id=id, title=title, year=year,
                aliases=aliases, players=players,
                playtime=playtime, description=description,
                thumbnail=thumbnail, image=image
            )

            yield game

