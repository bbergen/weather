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
DEFAULT_WIDTH = 30

RED = 1
GREEN = 2
YELLOW = 3
CYAN = 4

""" Encapsulates the current weather conditions
"""
class Current:
    def __init__(self, temp_c, temp_f, icon, windspeed, windDir, desc, humidity):
      self.temp_c = temp_c
      self.temp_f = temp_f
      self.icon = icon
      self.windspeed = windspeed
      self.windDir = windDir
      self.desc = desc
      self.humidity = humidity

    def display(self, screen, x):
      screen.addstr(3,x, "Current Conditions", curses.color_pair(YELLOW))
      screen.addstr(5,x, self.desc, curses.color_pair(GREEN))
      screen.addstr(6,x, "Temp C: " + self.temp_c)
      screen.addstr(7,x, "Temp F: " + self.temp_f)
      screen.addstr(8,x, "Windspeed: " + self.windspeed)
      screen.addstr(9,x, "Wind Dir: " + self.windDir)
      screen.addstr(10,x, "Humidity: " + self.humidity)
      #ascii_image(get_image(self.icon), screen)

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
      screen.addstr(starty, startx, "Forecast for " + self.date, curses.color_pair(YELLOW))
      screen.addstr(starty + 2, startx, self.desc, curses.color_pair(GREEN))
      screen.addstr(starty + 3, startx, "Minimum Temp: " + self.minTempC)
      screen.addstr(starty + 4, startx, "Maximum Temp: " + self.maxTempC)
      screen.addstr(starty + 5, startx, "UV Index: " + self.uvIndex)
      screen.addstr(starty + 6, startx, "Sunrise: " + self.sunrise)
      screen.addstr(starty + 7, startx, "Sunset: " + self.sunset)

""" Displays the retrieved results in an ncurses display
:params screen: ncurses screen to present upon
:params current: the current weather object
:params forecasts: a collection of retrieved forecasts
"""
def display(screen, current, forecasts):
  screen.clear()
  screen.border(0)
  display_title(screen)
  start_x = get_start_x(screen, len(forecasts))
  get_current_conditions(current).display(screen, start_x)
  start_x += DEFAULT_WIDTH
  for forecast in forecasts:
    forecast.display(screen, start_x, 3)
    start_x += DEFAULT_WIDTH
  screen.refresh()
  screen.getch() # pause the app until user input
  finalize_display()

""" Fetches the amount of horizontal space for each forecast
:param screen: The ncurses screen object
:param days: Number of days
:returns: 
"""
def get_start_x(screen, days):
  needed_width = (days + 1) * DEFAULT_WIDTH
  width = screen.getmaxyx()[1]
  return (width - needed_width) >> 1 #bit shifts are cooler than division

""" Draws the application title in the centre
:param screen: ncurses screen object to draw on
"""
def display_title(screen):
  y_x = screen.getmaxyx()
  mid = (y_x[1] - len(TITLE)) >> 1 #yay more shifts
  screen.addstr(1,mid, TITLE, curses.color_pair(RED))


""" Initializes the color settings
"""
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

""" Prints a message to the screen while data is fetched
:param screen: ncurses screen to write upon
"""
def print_loading(screen):
  y_x = screen.getmaxyx()
  loading = "Loading Weather Data..."
  l = len(loading)
  x = (y_x[1] - l) >> 1
  y = y_x[0] >> 1
  screen.border(0)
  display_title(screen)
  screen.addstr(y, x, loading, curses.color_pair(YELLOW))
  screen.refresh()

def main(stdscr, options):
    init_color_pairs()
    print_loading(stdscr)
    days = options.days if options.days != None else 0 
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
    display(stdscr, weather, forecasts)

if __name__ == "__main__":
  options = parse_options()
  try:
    curses.wrapper(main, options)
  except Exception as e:
    print "Error: Problem rendering weather results. Try increasing your terminal size"
    print e
