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
isodate = '%FT%H:%M:%S' #iso format for python strftime

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
                    info['datum_python'] = dateobj
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
    mdns = '{' + md + '}'
    root = etree.Element('rss', nsmap = {'md' : md})
    channel = etree.SubElement(root, 'channel')
    add_xml_children(channel,
            {'title' : 'Wahltermine',
             'link'  : FEEDLINK,
             'description' : 'Wahltermine',
             'generator'   : GENERATOR_URL,
             })

    for election in get_termine():
        termine = etree.SubElement(channel, 'item')
        add_xml_children(termine, {
            'title' : '%s Wahl %s' % (election['art'], election['land']),
            'link'  : FEEDLINK,
            'description' : 'Wahl',
            'guid' : 'wahl_%s_%s' % (election['land'], election['datum_str']),
            'category' : 'Wahl',
            'pubDate' : datetime.now().strftime('%F'),
            mdns + 'address' : election['land'],
            mdns + 'source_query_date' : datetime.now().strftime(isodate),
            })
        if election.get('datum_python', None):
            start_date = etree.SubElement(termine, mdns + 'start_date')
            start_date.text = election['datum_python'].strftime(isodate)
            end_date = etree.SubElement(termine, mdns + 'end_date')
            end_date.text = election['datum_python'].strftime(isodate)
    return root

if __name__ == '__main__':
    print "Content-type: text/xml"
    print ""
    print '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    print etree.tostring(generate_rss(), pretty_print = True)

