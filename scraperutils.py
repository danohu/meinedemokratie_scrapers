"""
Various bits and pieces, extending beautifulsoup
and the like
"""
from BeautifulSoup import NavigableString, BeautifulSoup
import re
from itertools import takewhile
import urllib2
import random
import string
import webbrowser

def tag_with_string(tag, pattern):
    return lambda item: item.name == tag and re.search(pattern, tagtext(item))

def soup_from_url(url):
    return BeautifulSoup(urllib2.urlopen(url).read())

def text_between(startPoint, endPoint, sep = ''):
    """This one might work!"""
    nextitems  = startPoint.nextGenerator()
    betweenList = list(takewhile(lambda x: x is not endPoint, nextitems))
    betweenText = [x for x in betweenList if isinstance(x, unicode)]
    filtered = [x for x in betweenText if 
                  x.__class__ is NavigableString #remove comments
                  and  not x.findParent('script')] #remove js
    return sep.join(betweenText)

def contents(tag, default = '', sep = ' '):
    """
    Return a unicode representation of the contents of a BS tag
    replace None &c with a default, recurse through nested tags, etc
    """
    if not tag:
        return default
    if not hasattr(tag, 'findAll'):
        return repr(tag)
    return sep.join(tag.findAll(text = re.compile('')))

def tableToArray(table, textOnly = True, *args, **kwargs):
   """
   Turns an html table into a 2-dimensional array, with each
   <td> or <th> represented by one element.
   Beware of using this on html tables with elements spanning multiple
   rows or multiple columns
   """
   lists = []
   try:
       for row in table.findAll('tr'):
           lists.append([x for x in row.findAll(['td', 'th'])])
       if not textOnly:
           return lists
   except AttributeError: #wasn't a real beautifulsoup object,probably None
       return lists
   textlists = []
   for row in lists:
       textlists.append([tagtext(x) for x in row])
   return textlists


def tagtext(element):
    items = []
    if not element:
        return ""
    elif isinstance(element, (unicode, str)):
        return element
    else:
        return ' '.join(x for x in element.recursiveChildGenerator() if isinstance(x, (unicode, str)))


def tidyText(text):
    subs = (
        ('&nbsp;', ''),
        ('\n+', '\n')
        )
    for (before, after) in subs:
        text = re.sub(before, after, text)
    return text

####These are just for my convenience in debugging

def savepage(content):
    filename = '/tmp/j%s.html' % ''.join(random.sample(string.lowercase, 4))
    f = open(filename, 'w')
    f.write(content)
    f.close()
    webbrowser.open(filename)
