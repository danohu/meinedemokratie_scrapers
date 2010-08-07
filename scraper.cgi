#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from BeautifulSoup import BeautifulSoup
from scraperutils import *
import re
from datetime import datetime
from lxml import etree
import cgi


"""
Requires:
  BeautifulSoup (included here, to avoid weird versioning requirements)
  lxml
"""

monthnames_de = [u'januar', u'februar', u'm\xe4rz', u'april', u'mai', u'juni', u'juli', u'august', u'september', u'oktober', u'november', u'dezember']

FEEDLINK = 'http://www.wahlrecht.de/termine.htm'
GENERATOR_URL = 'http://github.com/danohuiginn/wahltermine_scraper'

def replace_monthname(instr):
        """turn e.g. März --> 3"""
        instr = tidyText(instr.lower())
        for num, monthname in enumerate(monthnames_de):
            instr = instr.replace(monthname, str(num + 1))
        return instr

def get_termine():
    wahldata = []
    soup = BeautifulSoup(urllib2.urlopen(FEEDLINK).read())
    terminere = re.compile('termine-(\d{4})')
    for tbody in soup.findAll('tbody', id = terminere):
        year = terminere.search(tbody['id']).group(1)
        for row in tbody.findAll('tr'):
            cells = [tidyText(tagtext(x)) for x in row.findAll('td')]
            info = {
              'jahr' : year,
              'datum_str' : cells[1],
              'land' : cells[2],
              'art'  : cells[3],
              'turnus' : cells[4],
              }
            datestr = '%s %s' % (year, replace_monthname(info['datum_str']))
            for dateformat in ('%Y %d. %m', '%Y %d.%m'):
                try:
                    dateobj = datetime.strptime(datestr, dateformat)
                    info['date_formatted'] = dateobj.strftime('%F')
                    break
                except Exception:
                    continue
            wahldata.append(info)
    return wahldata

def add_xml_children(parent, datadict):
    for key, value in datadict.items():
        subitem = etree.SubElement(parent, key)
        subitem.text = value
    return parent

def generate_rss():
    md = 'http://www.meine-demokratie.de'
    root = etree.Element('rss', nsmap = {'md' : md})
    channel = etree.SubElement(root, 'channel')
    add_xml_children(channel,
            {'title' : 'Walhtermine',
             'link'  : FEEDLINK,
             'description' : 'Wahltermine',
             'generator'   : GENERATOR_URL,
             '{http://www.w3.org/1999/xhtml}body' : 'ABC',
             '{%s}source_query_date' % md : datetime.now().strftime('%FT%H%M%S'),
             })
    for election in get_termine():
        termine = etree.SubElement(channel, 'item')
        add_xml_children(termine, {
            'title' : '%s Wahlen, %s' % (election['art'], election['land']),
            'link'  : FEEDLINK,
            'description' : '',
            'pubDate' : datetime.now().strftime('%F')})
    return root

if __name__ == '__main__':
    print "Content-type: text/xml"
    print etree.tostring(generate_rss(), pretty_print = True)

