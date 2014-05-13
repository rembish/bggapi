from urllib import quote
from urllib2 import urlopen
from xml.etree.cElementTree import parse

from bggapi.boardgame import BoardGame


BASE_URL = 'http://www.boardgamegeek.com/xmlapi'


def search(title, exact=False):
    url = '%s/search?search=%s&exact=%d' % (
        BASE_URL, quote(str(title)), 1 if exact else 0)

    root = parse(urlopen(url)).getroot()
    ids = [game.attrib['objectid'] for game in root.iter("boardgame")]
    return _fetch(ids) if ids else []


def _fetch(ids):
    ids = [str(bgg_id) for bgg_id in ids]
    url = '%s/boardgame/%s?stats=1' % (BASE_URL, ','.join(ids))
    root = parse(urlopen(url)).getroot()

    games = []
    for boardgame in root.iter("boardgame"):
        if 'objectid' not in boardgame.attrib:
            continue

        game = BoardGame(boardgame)
        games.append(game)

    return sorted(games, key=lambda x: x.id)
