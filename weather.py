#!/usr/bin/python2
import urllib2
import pygeoip


def get_ip():
    return urllib2.urlopen('http://ip.42.pl/raw').read()

def get_location_record(ip):
    geo_con = pygeoip.GeoIP('/opt/GeoIP/GeoIP.dat')
    return geo_con.record_by_addr(ip)

def main():
    ip = get_ip()
    print str(ip)
    record = get_location_record(ip)
    city = record['city']
    region = record['region_code']
    country = record['country_name']
    print str(city) + ", " + str(region) + ", " + str(country)

if __name__ == "__main__":
    main()
