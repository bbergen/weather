#!/usr/bin/python2
# Bryan Bergen - 300173752
"""
This script will display the current weather conditions and up
to 5 days of forecasts based on the location passed in on the 
command line. Location can be passed as a city name, zip code,
or Canadian postal code.
If no location is passed, the script will look up the current
location based on public IP address. 
Type ./weather.py --help for more information
"""
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
DEFAULT_WIDTH = 40
DEFAULT_HEIGHT = 26
START_HEIGHT = 3

RED = 1
GREEN = 2
YELLOW = 3
CYAN = 4

class Forecast:
    """ Encapsulation of a forecast
    """
    def __init__(self, date, minTempC, maxTempC, uvIndex, sunrise, sunset, desc, icon):
      self.date = date
      self.minTempC = minTempC
      self.maxTempC = maxTempC
      self.uvIndex = uvIndex
      self.sunrise = sunrise
      self.sunset = sunset
      self.desc = desc
      self.icon = icon

    def display_image(self, screen, x, y):
      ascii_image(get_image(self.icon), screen, x, y)

    def display(self, screen, x, y):
      screen.addstr(y, x, "Forecast for " + self.date, curses.color_pair(YELLOW))
      screen.addstr(y + 2, x, self.desc, curses.color_pair(GREEN))
      screen.addstr(y + 3, x, "Min Temp C: " + self.minTempC)
      screen.addstr(y + 4, x, "Max Temp C: " + self.maxTempC)
      screen.addstr(y + 5, x, "UV Index: " + self.uvIndex)
      screen.addstr(y + 6, x, "Sunrise: " + self.sunrise)
      screen.addstr(y + 7, x, "Sunset: " + self.sunset)

class Current(Forecast):
    """ Encapsulates the current weather conditions
    Extends from Forecast
    """
    def __init__(self, temp_c, temp_f, icon, windspeed, windDir, desc, humidity):
      self.temp_c = temp_c
      self.temp_f = temp_f
      self.icon = icon
      self.windspeed = windspeed
      self.windDir = windDir
      self.desc = desc
      self.humidity = humidity

    def display(self, screen, x, y):
      screen.addstr(y, x, "Current Conditions", curses.color_pair(YELLOW))
      screen.addstr(y + 2, x, self.desc, curses.color_pair(GREEN))
      screen.addstr(y + 3, x, "Temp C: " + self.temp_c)
      screen.addstr(y + 4, x, "Temp F: " + self.temp_f)
      screen.addstr(y + 5, x, "Windspeed: " + self.windspeed)
      screen.addstr(y + 6, x, "Wind Dir: " + self.windDir)
      screen.addstr(y + 7, x, "Humidity: " + self.humidity)

def display(screen, current, forecasts, icons):
  """ Displays the retrieved results in an ncurses display
  :params screen: ncurses screen to present upon
  :params current: the current weather object
  :params forecasts: a collection of retrieved forecasts
  :params icons: if the icons should be displayed
  """
  screen.clear()
  screen.border(0)
  display_title(screen)
  display_map = map_forecasts(screen, current, forecasts, icons)
  for key in display_map:
    display_map[key].display(screen, key[0], key[1])
    if icons:
      display_map[key].display_image(screen, key[0], key[1] + 10)
  screen.refresh()
  screen.getch() # pause the app until user input
  finalize_display()

def map_forecasts(screen, current, forecasts, icons):
  """ Maps each forcast to an x,y coordinate
  :param screen: The ncurses screen object
  :param forecasts: The series of forecasts
  :param current: The current weather conditions
  :param icons: if icons are to be shown
  :returns: a map of (x,y) tuples to forecasts
  """
  map = {}
  screen_width = screen.getmaxyx()[1]
  needed_width = DEFAULT_WIDTH if icons else 30
  per_row = screen_width / needed_width
  x = (screen_width - needed_width * per_row) >> 1
  y = START_HEIGHT
  map[(x,y)] = current
  for forecast in forecasts:
    x += needed_width
    if x + needed_width > screen_width:
      x = (screen_width - needed_width * per_row) >> 1
      add_y = DEFAULT_HEIGHT if icons else 10
      y += add_y
    map[(x,y)] = forecast
  return map

def display_title(screen):
  """ Draws the application title in the centre
  :param screen: ncurses screen object to draw on
  """
  y_x = screen.getmaxyx()
  mid = (y_x[1] - len(TITLE)) >> 1 
  screen.addstr(1,mid, TITLE, curses.color_pair(RED))

def init_color_pairs():
  """ Initializes the color settings
  """
  curses.start_color()
  curses.use_default_colors()
  curses.init_pair(RED, curses.COLOR_RED, -1)
  curses.init_pair(GREEN, curses.COLOR_GREEN, -1)
  curses.init_pair(YELLOW, curses.COLOR_YELLOW, -1)
  curses.init_pair(CYAN, curses.COLOR_CYAN, -1)

def init_screen():
  """ Initializes the ncurses tools
  """
  screen = curses.initscr()
  curses.noecho()
  init_color_pairs()
  return screen

def finalize_display():
  """ Returns screen to default state
  """
  curses.echo()
  curses.endwin()

def get_image(url):
  """ Fetches an image from a url
  :param url: url of the image 
  :returns: a file descriptor to the image
  """
  imageReq = urllib2.Request(url)
  imageUrl = urllib2.urlopen(imageReq)
  image = io.BytesIO(imageUrl.read())
  return image

def ascii_image(i, screen, start_x, start_y):
    """ Converts an image to ascii, and draws in on screen
    :params i: the image to convert
    :params screen: an ncurses screen object to draw upon
    :params start_x: x axis location to start drawing
    :params start_y: y axis location to start drawing
    """
    tones = [
        " ",
        " ",
        ".,",
        "_ivc=!/|\\~",
        "gjez2]/(YL)t[+T7Vf",
        "mdK4ZGbNDXY5P*Q",
        "W8KMA",
        "#%$"]
    bounds = [
        36, 72, 108, 144, 180, 216, 252]
    image = Image.open(i)
    image = image.resize((30, 15), Image.BILINEAR)
    image = image.convert("L")
    for y in range(0, image.size[1]):
      str = ""
      for x in range(0, image.size[0]):
        bright = 255 - image.getpixel((x, y))
        row = bisect(bounds, bright)
        possible = tones[row]
        str = str + possible[random.randint(0, len(possible) - 1)]
      screen.addstr(y + start_y, start_x, str, curses.color_pair(GREEN))

def get_forecasts(json_result, days):
    """ Parses a json object for a list of forecasts
    :param json_result: Json response from weather api
    :param days: number of days requested
    :returns: a collection of Weather objects
    """
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
        icon = weather['hourly'][3]['weatherIconUrl'][0]['value']
        forecast = Forecast(date, min_temp, max_temp, uv_index, sunrise, sunset, desc, icon)
        forecast_range.append(forecast)
    return forecast_range

def get_weather(latlong, city, zip, pc, days):
    """ Queries weather server with lat, long
    :param lat: latitude of weather query target
    :param long: longitude of weather query target
    :param city: location of query
    :param zip: location of query
    :param pc: location of query
    :param days: number of days (1-5) of forecast
    :returns: a JSON object containing weather data for target
    """
    latlong = "" if latlong == None else latlong
    city = "" if city == None else city
    zip = "" if zip == None else zip
    pc = "" if pc == None else pc
    location = "q=" + latlong + city + zip + pc
    weather_url = PREFIX + location + FORMAT + "&num_of_days=" + str(days) + KEY
    response = urllib2.urlopen(weather_url).read()
    return json.loads(response)

def get_ip():
    """ Fetches the current public IP 
    :returns: A string with the local host's public IP
    """
    return urllib2.urlopen(IP_FETCH).read()

def get_location_record(ip):
    """ Fetches a Record from the GeoIP database
    :param ip: The ip address to lookup in GeoIP
    :returns: A matching record from the database
    """
    geo_con = pygeoip.GeoIP('/opt/GeoIP/GeoIP.dat')
    return geo_con.record_by_addr(ip)

def get_current_conditions(json_result):
    """ Parses the json weather result for the current conditions
    :param json_result: json object from weather api
    :returns: the results encapsulated in a Current object
    """
    current = json_result['data']['current_condition'][0]
    cur_weather = Current(current['temp_C'], \
        current['temp_F'], \
        current['weatherIconUrl'][0]['value'], \
        current['windspeedKmph'], \
        current['winddir16Point'], \
        current['weatherDesc'][0]['value'], \
        current['humidity'])
    return cur_weather

def parse_options():
    """ Parses command line options and handles errors
    :returns: An options object containing commandline arguments
    """
    parser = optparse.OptionParser('%prog ' + '[-i] ' + \
        '[-c <city> | -z <zipcode> | ' + \
        '-p <postal code>] [-d <days of forecast>]')
    parser.add_option('-c', dest='city', type='string', \
        help='Target for remote forecast')
    parser.add_option('-z', dest='zip', type='string', \
        help='Target for remote forecast')
    parser.add_option('-p', dest='pc', type='string', \
        help='Target for remote forecast')
    parser.add_option('-d', dest='days', type='int', \
        help='Quantity of future forecasting. max 5')
    parser.add_option('-i', dest='icons', default=False, \
        action='store_true', \
        help='Displays ascii icons of the weather. Requires a large terminal')
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

def format_city(city):
  """ Formats the city string for the weather api url
  :param city: The city name as entered by user
  :returns: The city name stripped of spaces
  """
  if city != None:
    return city.replace(' ', '+')
  else:
    return None

def print_loading(screen):
  """ Prints a message to the screen while data is fetched
  :param screen: ncurses screen to write upon
  """
  y_x = screen.getmaxyx()
  loading = "Loading Weather Data..."
  l = len(loading)
  x = (y_x[1] - l) >> 1
  y = y_x[0] >> 1
  screen.border(0)
  display_title(screen)
  screen.addstr(y, x, loading, curses.color_pair(YELLOW))
  screen.leaveok(1)
  screen.refresh()

def main(stdscr, options):
    """ Main Entry Point when running as script
    :param stdscr: ncurses screen object
    :param options: commandline args
    """
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
      city = record['city']
    weather = get_weather(latlong, city, zip, pc, days)
    forecasts = get_forecasts(weather, days)
    current_weather = get_current_conditions(weather)
    display(stdscr, current_weather, forecasts, options.icons)

if __name__ == "__main__":
  options = parse_options()
  try:
    curses.wrapper(main, options)
  except Exception as e:
    print "Error: Problem rendering weather results. Try increasing your terminal size or choose less days"
    print e
