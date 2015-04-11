#!/usr/bin/python2
# Bryan Bergen - 300173752
from datetime import date
from pprint import pprint
from PIL import Image
from bisect import bisect
import curses
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
TITLE = "Welcome to Bryan's Weather App"

RED = 1
GREEN = 2
YELLOW = 3
CYAN = 4

class Current:
    def __init__(self, temp_c, temp_f, icon, windspeed, windDir, desc, humidity):
      self.temp_c = temp_c
      self.temp_f = temp_f
      self.icon = icon
      self.windspeed = windspeed
      self.windDir = windDir
      self.desc = desc
      self.humidity = humidity

    def display(self, screen):
      screen.addstr(3,2, "Current Conditions", curses.color_pair(YELLOW))
      screen.addstr(5,2, "Description: " + str(self.desc))
      screen.addstr(6,2, "Temp C: " + str(self.temp_c))
      screen.addstr(7,2, "Temp F: " + str(self.temp_f))
      screen.addstr(8,2, "Windspeed: " + str(self.windspeed))
      screen.addstr(9,2, "Wind Dir: " + str(self.windDir))
      screen.addstr(10,2, "Humidity: " + str(self.humidity))
      ascii_image(get_image(self.icon), screen)

    def __str__(self):
      rtn = "--Current conditions--\n" + \
      "Description: " + str(self.desc) + "\n" + \
      "Temp C: " + str(self.temp_c) + "\n" + \
      "Temp F: " + str(self.temp_f) + "\n" + \
      "Windspeed: " + str(self.windspeed) + "\n" + \
      "Wind Direction: " + str(self.windDir) + "\n" + \
      "Humidity: " + str(self.humidity) + "\n" 
      return rtn

""" Encapsulation of a forecast
"""
class Forecast:
    def __init__(self, date, minTempC, maxTempC, uvIndex, sunrise, sunset, desc, icon):
      self.date = date
      self.minTempC = minTempC
      self.maxTempC = maxTempC
      self.uvIndex = uvIndex
      self.sunrise = sunrise
      self.sunset = sunset
      self.desc = desc
      self.icon = icon

    def display(self, screen, startx, starty):
      screen.addstr(starty, startx, "Testing...")

    def __str__(self):
      rtn = "Forecast for: " + self.date + "\n" + \
          "Description: " + self.desc + "\n" + \
          "Max Temp: " + self.maxTempC + "\n" + \
          "Min Temp: " + self.minTempC + "\n" + \
          "UV Index: " + self.uvIndex + "\n" + \
          "Sunrise: " + self.sunrise + "\n" + \
          "Sunset: " + self.sunset + "\n" 
      return "------------------------\n" + rtn

def display(current, forecasts):
  screen = init_screen()
  screen.border(0)
  display_title(screen)
  get_current_conditions(current).display(screen)
  screen.refresh()
  screen.getch()
  finalize_display()
  #for forecast in forecasts:
  #  print forecast

""" Draws the application title in the centre
:param screen: ncurses screen object to draw on
"""
def display_title(screen):
  y_x = screen.getmaxyx()
  mid = (y_x[1] >> 1) - (len(TITLE) >> 1)
  screen.addstr(1,mid, TITLE, curses.color_pair(RED))

def init_color_pairs():
  curses.start_color()
  curses.use_default_colors()
  curses.init_pair(RED, curses.COLOR_RED, -1)
  curses.init_pair(GREEN, curses.COLOR_GREEN, -1)
  curses.init_pair(YELLOW, curses.COLOR_YELLOW, -1)
  curses.init_pair(CYAN, curses.COLOR_CYAN, -1)

""" Initializes the ncurses tools
"""
def init_screen():
  screen = curses.initscr()
  curses.noecho()
  init_color_pairs()
  return screen

""" Returns screen to default state
"""
def finalize_display():
  curses.echo()
  curses.endwin()

""" Fetches an image from a url
:param url: url of the image 
:returns: a file descriptor to the image
"""
def get_image(url):
    imageReq = urllib2.Request(url)
    imageUrl = urllib2.urlopen(imageReq)
    image = io.BytesIO(imageUrl.read())
    return image

""" Converts an image to ascii, and draws in on screen
:params i: the image to convert
:params screen: an ncurses screen object to draw upon
"""
def ascii_image(i, screen):
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
    image = Image.open(i)
    image = image.resize((80, 40), Image.BILINEAR)
    image = image.convert("L")
    str = ""
    for y in range(0, image.size[1]):
      for x in range(0, image.size[0]):
        bright = 255 - image.getpixel((x, y))
        row = bisect(bounds, bright)
        possible = tones[row]
        str = str + possible[random.randint(0, len(possible) - 1)]
      screen.addstr(y + 15, 2, str, curses.color_pair(CYAN))
      str = ""

""" Parses a json object for a list of forecasts
:param json_result: Json response from weather api
:param days: number of days requested
:returns: a collection of Weather objects
"""
def get_forecasts(json_result, days):
    raw_forecasts = json_result['data']['weather']
    forecast_range = []
    if days > 0:
      for day in range(days):
        weather = raw_forecasts[day]
        min_temp = weather['mintempC']
        max_temp = weather['maxtempC']
        uv_index = weather['uvIndex']
        sunrise = weather['astronomy'][0]['sunrise']
        sunset = weather['astronomy'][0]['sunset']
        date = weather['date']
        desc = weather['hourly'][0]['weatherDesc'][0]['value']
        icon = weather['hourly'][0]['weatherIconUrl'][0]['value']
        forecast = Forecast(date, min_temp, max_temp, uv_index, sunrise, sunset, desc, icon)
        forecast_range.append(forecast)
    return forecast_range

""" Queries weather server with lat, long
:param lat: latitude of weather query target
:param long: longitude of weather query target
:param city: location of query
:param zip: location of query
:param pc: location of query
:param days: number of days (1-5) of forecast
:returns: a JSON object containing weather data for target
"""
def get_weather(latlong, city, zip, pc, days):
    latlong = "" if latlong == None else latlong
    city = "" if city == None else city
    zip = "" if zip == None else zip
    pc = "" if pc == None else pc
    location = "q=" + latlong + city + zip + pc
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

""" Parses the json weather result for the current conditions
:param json_result: json object from weather api
:returns: the results encapsulated in a Current object
"""
def get_current_conditions(json_result):
    current = json_result['data']['current_condition'][0]
    cur_weather = Current(current['temp_C'], \
        current['temp_F'], \
        current['weatherIconUrl'][0]['value'], \
        current['windspeedKmph'], \
        current['winddir16Point'], \
        current['weatherDesc'][0]['value'], \
        current['humidity'])
    return cur_weather

""" Parses command line options and handles errors
:returns: An options object containing commandline arguments
"""
def parse_options():
    parser = optparse.OptionParser('%prog ' + \
        '[-c <city> | -z <zipcode> | ' + \
        '-p <postal code>] [-d <days of forecast>]')
    parser.add_option('-c', dest='city', type='string', \
        help='target for remote forecast')
    parser.add_option('-z', dest='zip', type='string', \
        help='target for remote forecast')
    parser.add_option('-p', dest='pc', type='string', \
        help='target for remote forecast')
    parser.add_option('-d', dest='days', type='int', \
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

""" Formats the city string for the weather api url
:param city: The city name as entered by user
:returns: The city name stripped of spaces
"""
def format_city(city):
  if city != None:
    return city.replace(' ', '+')
  else:
    return None

def main():
    options = parse_options()
    days = options.days if options.days != None else 1 
    city = format_city(options.city)
    zip = options.zip
    pc = options.pc
    latlong = None
    if city == None and zip == None and pc == None:
      ip = get_ip()
      record = get_location_record(ip)
      lat = record['latitude']
      long = record['longitude']
      latlong = str(lat) + "," + str(long)
    weather = get_weather(latlong, city, zip, pc, days)
    forecasts = get_forecasts(weather, days)
    display(weather, forecasts)

if __name__ == "__main__":
    main()
