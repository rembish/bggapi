from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser


class CachedProperty(object):
    _missing = type("Missing")()

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        value = instance.__dict__.get(self.__name__, self._missing)
        if value is self._missing:
            value = self.func(instance)
            instance.__dict__[self.__name__] = value

        return value


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
