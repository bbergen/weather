#!/usr/bin/python2
import urllib2
import pygeoip

def get_json(lat, long):
    weather_url = "http://api.openweathermap.org/data/2.5/weather?" \
            + "lat=" + str(lat) \
            + "&lon=" + str(long)
    response = urllib2.urlopen(weather_url).read()
    return response

def get_ip():
    return urllib2.urlopen('http://ip.42.pl/raw').read()

def get_location_record(ip):
    geo_con = pygeoip.GeoIP('/opt/GeoIP/GeoIP.dat')
    return geo_con.record_by_addr(ip)

def main():
    ip = get_ip()
    print str(ip)
    record = get_location_record(ip)
    lat = record['latitude']
    long = record['longitude']
    print get_json(lat, long)

if __name__ == "__main__":
    main()
