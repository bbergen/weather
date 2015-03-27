#!/usr/bin/python2
from datetime import date
from pprint import pprint
import datetime
import urllib2
import pygeoip
import json

KEY = "&key=ce5515ba976cc6b7e8a09c7171123"
PREFIX = "https://api.worldweatheronline.com/free/v2/weather.ashx?"
FORMAT = "&format=json"
IP_FETCH = "http://myexternalip.com/raw"

""" Queries weather server with lat, long
:param lat: latitude of weather query target
:param long: longitude of weather query target
:returns: a JSON object containing weather data for target
"""
def get_json(lat, long):
    location = "q=" + str(lat) + "," + str(long)
    weather_url = PREFIX + location + FORMAT + "&num_of_days=1" + KEY
    response = urllib2.urlopen(weather_url).read()
    return json.loads(response)

""" Fetches the current public IP 
:returns: A string with the local host's public IP
"""
def get_ip():
    return urllib2.urlopen(IP_FETCH).read()

""" Fetches a Record from the GeoIP database
:param ip: The ip address to lookup in GeoIP
:returns: A matching record from the database
"""
def get_location_record(ip):
    geo_con = pygeoip.GeoIP('/opt/GeoIP/GeoIP.dat')
    return geo_con.record_by_addr(ip)

""" Prints the weather results to console
:param json_result: A JSON object containing weather results
"""
def print_weather(json_result):
    print "Weather for " + str(date.today())
    print "Current Time: " \
            + datetime.datetime.now().strftime('%H:%M:%S')
    data = json_result['data']
    print type(data)
    current = data['current_condition'][0]
    print type(current)
    print current['weatherIconUrl'][0]['value']

def main():
    ip = get_ip()
    print str(ip)
    record = get_location_record(ip)
    lat = record['latitude']
    long = record['longitude']
    print_weather(get_json(lat, long))

if __name__ == "__main__":
    main()
