#!/usr/bin/python2
# Bryan Bergen - 300173752
from datetime import date
from pprint import pprint
from PIL import Image
from bisect import bisect
import PIL.ImageOps
import random
import datetime
import urllib2
import io
import pygeoip
import json
import optparse

KEY = "&key=ce5515ba976cc6b7e8a09c7171123"
PREFIX = "https://api.worldweatheronline.com/free/v2/weather.ashx?"
FORMAT = "&format=json"
IP_FETCH = "http://myexternalip.com/raw"

""" Enum-Like type to define console output modifiers
"""
class Font:
  BLUE = '\033[1;96m'
  RED = '\033[1;91m'
  GREEN = '\033[1;92m'
  YELLOW = '\033[1;93m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'

""" Fetches an image from a url
:param url: url of the image 
:returns: a file descriptor to the image
"""
def get_image(url):
    imageReq = urllib2.Request(url)
    imageUrl = urllib2.urlopen(imageReq)
    image = io.BytesIO(imageUrl.read())
    return image

""" Converts an image to ascii
:params i: the image to convert
:returns: a string containing the ascii
"""
def ascii_image(i):
    tones = [
        " ",
        " ",
        ".,-",
        "_ivc=!/|\\~",
        "gjez2]/(YL)t[+T7Vf",
        "mdK4ZGbNDXY5P*Q",
        "W8KMA",
        "#%$"]
    bounds = [
        36, 72, 108, 144, 180, 216, 252]
    print type(i)
    image = Image.open(i)
    image = image.resize((100, 50), Image.BILINEAR)
    image = image.convert("L")
    str = ""
    for y in range(0, image.size[1]):
      for x in range(0, image.size[0]):
        bright = 255 - image.getpixel((x, y))
        row = bisect(bounds, bright)
        possible = tones[row]
        str = str + possible[random.randint(0, len(possible) - 1)]
      str = str + '\n'
    return str


""" Queries weather server with lat, long
:param lat: latitude of weather query target
:param long: longitude of weather query target
:param days: number of days (1-5) of forecast
:returns: a JSON object containing weather data for target
"""
def get_weather(lat, long, days):
    location = "q=" + str(lat) + "," + str(long)
    weather_url = PREFIX + location + FORMAT + "&num_of_days=" + str(days) + KEY
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
    image = get_image(current['weatherIconUrl'][0]['value'])
    print ascii_image(image)
    pprint(json_result)

""" Parses command line options and handles errors
:returns: An options object containing commandline arguments
"""
def parse_options():
    parser = optparse.OptionParser('usage%prog ' + \
        '[-c <city> | -z <zipcode> | ' + \
        '-p <postal code>] [-f <days of forecast>]')
    parser.add_option('-c', dest='city', type='string', \
        help='target for remote forecast')
    parser.add_option('-z', dest='zip', type='string', \
        help='target for remote forecast')
    parser.add_option('-p', dest='pc', type='string', \
        help='target for remote forecast')
    parser.add_option('-f', dest='days', type='int', \
        help='quantity of future forecasting. max 5')
    (options, args) = parser.parse_args()
    c = options.city == None
    z = options.zip == None
    p = options.pc == None
    f = options.days == None
    if not f and (options.days > 5 or options.days < 1):
      print "Error: Forecast must be between 1 and 5 days"
      parser.print_usage()
      exit()
    if not c and not z:
      parser.print_usage()
      exit()
    elif not c and not p:
      parser.print_usage()
      exit()
    elif not z and not p:
      parser.print_usage()
      exit()
    else:
      return options

def main():
    options = parse_options()
    print options
    ip = get_ip()
    print Font.RED + str(ip) + Font.END
    print Font.YELLOW + "Hello World" + Font.END
    record = get_location_record(ip)
    print str(record['city'])
    lat = record['latitude']
    long = record['longitude']
    days = options.days if options.days != None else 1 
    weather = get_weather(lat, long, days)
    print_weather(weather)

if __name__ == "__main__":
    main()
