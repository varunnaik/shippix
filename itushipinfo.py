# http://www.udxf.nl/ITU-ship-classifications.pdf

from itu_classifications import classifications 
import requests
import re

def get_ship_class(term):
    return terms[term]

def get_vessel_details_url(mmsi):
    # look up vessel name from the vessel's Mobile Maritime Subscriber Identifier (mmsi)
    data = {
            'lang':'en',
            'lgg':7,
            'p':1,
            'sh_name':'',
            'sh_callsign':'',
            'sh_mmsi': mmsi,
            'cgaid':0,
            'sh_epirb_id':'',
            'sh_epirb_hex':'',
            'sh_imo_nbr':''
    }
    r = requests.post('http://www.itu.int/online/mms/mars/ship_search.sh', data=data)
    url = re.findall('\<A HREF=ship_detail.sh([^\>]*)\>', r.text)
    if url:
        return 'http://www.itu.int/online/mms/mars/ship_detail.sh'+url[0]
    else:
        return None

def get_vessel_details(url):
    details = {
        'name': '',
        'flag': '',
        'gross_tonnage': '',
        'url': url,
        'details': '',
        'size': '',
        'notes': ''
    }
    r = requests.get(url)
    try:
        details['name'] = re.findall('Ship Name(?:\<[^\>]*\>[:\s]*)*([^\<]*)', r.text)[0]
    except IndexError: pass
    try:
        details['flag'] = re.findall('Geo. Area(?:\<[^\>]*\>[:\s]*)*([^\<]*)', r.text)[0]
    except IndexError: pass
    try:
        details['gross_tonnage'] = re.findall('Gross Tonnage(?:\<[^\>]*\>[:\s]*)*([^\<]*)', r.text)[0]
    except IndexError: pass
    try:
        ship_class = re.findall('Ship class(?:\<[^\>]*\>[:\s]*)*([^\<]*)', r.text)[0]
        details['details']=" / ".join(map(lambda x: classifications[x] if x in classifications else x, filter(lambda x: len(x) == 2 or len(x)==3, ship_class.split(' '))))
    except IndexError: pass    
    try:
        persons = re.findall('Person Capacity(?:\<[^\>]*\>[:\s]*)*([^\<]*)', r.text)[0]
        if persons:
            details['notes'] = 'Person capacity: ' + persons
    except IndexError: pass


    return details

def itu_identify_vessel(ais):
    url = get_vessel_details_url(ais['mmsi'])
    if not url:
        return None
    return get_vessel_details(url)
