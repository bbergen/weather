#!/usr/bin/python2
import urllib2

def get_ip():
    return urllib2.urlopen('http://ip.42.pl/raw').read()

def main():
    ip = get_ip()
    print str(ip)

if __name__ == "__main__":
    main()
