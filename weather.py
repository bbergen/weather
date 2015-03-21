#!/usr/bin/python2
from datetime import date
from pprint import pprint
import datetime
import urllib2
import pygeoip
import json

def get_json(lat, long):
    weather_url = "http://api.openweathermap.org/data/2.5/weather?" \
            + "lat=" + str(lat) \
            + "&lon=" + str(long)
    response = urllib2.urlopen(weather_url).read()
    return json.loads(response)

def get_ip():
    return urllib2.urlopen('http://ip.42.pl/raw').read()

def get_location_record(ip):
    geo_con = pygeoip.GeoIP('/opt/GeoIP/GeoIP.dat')
    return geo_con.record_by_addr(ip)

def print_weather(json_result):
    print "Weather for " + str(date.today())
    print "Current Time: " \
            + datetime.datetime.now().strftime('%H:%M:%S')
    pprint(json_result)

def main():
    ip = get_ip()
    print str(ip)
    record = get_location_record(ip)
    lat = record['latitude']
    long = record['longitude']
    print_weather(get_json(lat, long))

if __name__ == "__main__":
    main()
