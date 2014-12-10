#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Meteo Reporter - deltaHacker Magazine - v.1.0
# Copyright (c) 2014, Petros Kyladitis
#
# Prints reports for hazardous weather conditions, predicted from meteo.gr,
# at EPSON thermal printers, connected at a RaspberrPi board, using escpos library.
#
# This is free software, distributed under the GNU GPL 3

import re, urllib
from escpos import *

# Options section start
MIN_TEMP = 3
MAX_TEMP = 37
MAX_WIND_SPEED = 7
HAZARD_CONDITIONS = ["XIONOPTOSI","KATAIGIDA"] #you can use the values: "KATHAROS", "ARAII SYNNEFIA", "LIGA SYNNEFA", "ARKETA SYNNEFA", "SYNNEFIASMENOS", "PERIORISMENI ORATOTITA", "ASTHENIS BROXI", "BROXI", "KATAIGIDA", "XIONONERO" & "XIONOPTOSI"
CITY = "ΧΙΟΣ" #City name
URL = "http://meteo.gr/m/m-cf.cfm?city_id=11&ProvinceID=8" #City's URL
PRINTER_TYPE = "USB" #you can select between "USB", "SERIAL" & "NET" values
USB_PRINTER_VENDOR_ID = 0x04b8 #In case of USB printer
USB_PRINTER_PRODUCT_ID = 0x0e03 #In case of USB printer
NETWORK_PRINTER_IP = "192.168.1.99" #In case of network printer
SERIAL_PRINTER_PORT = "/dev/tty0" #In case of serial printer
# Options section end

def strip_tags(html):
    return re.sub('<[^<]+?>', '', html)
    
def el_to_lat(text):
    el = ('α','β','γ','δ','ε','ζ','η','θ','ι','κ','λ','μ','ν','ξ','ο','π','ρ','σ','τ','υ','φ','χ','ψ','ω','Α','Β','Γ','Δ','Ε','Ζ','Η','Θ','Ι','Κ','Λ','Μ','Ν','Ξ','Ο','Π','Ρ','Σ','Τ','Υ','Φ','Χ','Ψ','Ω','ς','ά','έ','ή','ί','ϊ','ΐ','ό','ύ','ϋ','ΰ','ώ','Ά','Έ','Ή','Ί','Ϊ','Ό','Ύ','Ϋ','Ώ')
    lat = ('a','b','g','d','e','z','i','th','i','k','l','m','n','ks','o','p','r','s','t','y','f','x','ps','o','A','B','G','D','E','Z','I','TH','I','K','L','M','N','KS','O','P','R','S','T','Y','F','X','PS','O','s','a','e','i','i','i','i','o','y','y','y','o','A','E','I','I','I','O','Y','Y','O')
    dic = dict(zip(el, lat))

    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

def main():
    opener = urllib.FancyURLopener({})
    f = opener.open(URL)
    content = f.read()
    start = content.find(CITY) + len(CITY)
    end = content.find("<style>", start)
    htmltext = content[start:end]
    plaintext = strip_tags(htmltext)
    plaintext = plaintext.replace(" &deg;C", "^C")
    plaintext = plaintext.replace(" μποφόρ", "^BF")
    lines = plaintext.splitlines(True)
    listedlines = []

    for line in lines:
        line = line.strip()
        if line != "":
            listedlines.append(line)
            
    i = 0
    printline = ""
    printdoc = ""
    forecast = [""] * 5

    for listedline in listedlines:
        forecast[i] = el_to_lat(listedline).upper()
        
        if i == 4:
            printable = False
            
            if int(forecast[2][0:forecast[2].find("^")]) <= MIN_TEMP or int(forecast[2][0:forecast[2].find("^")]) >= MAX_TEMP:
                printable = True

            if forecast[3] in HAZARD_CONDITIONS:
                printable = True

            if  int(forecast[4][:forecast[4].find("^")]) >= MAX_WIND_SPEED:
                printable = True

            if printable == True:
                for forecastItem in forecast:
                    printline = printline + " " + forecastItem
                printdoc = printdoc + printline.strip() + "\n"
            
            printline = ""
            i = 0
        else:
            i = i + 1

    if printdoc != "":
        Epson = None
        if PRINTER_TYPE == "USB":
            Epson = printer.Usb(USB_PRINTER_VENDOR_ID,USB_PRINTER_PRODUCT_ID)
        elif PRINTER_TYPE == "NET":
            Epson = printer.Network(NETWORK_PRINTER_IP)
        else:
            Epson = printer.Serial(SERIAL_PRINTER_PORT)
        Epson.set("LEFT", "A", "B", 1, 1)
        Epson.text("## HAZARDOUS WEATHER REPORT FOR " + el_to_lat(CITY) + " ##\n")
        Epson.text(printdoc)
        Epson.text("\n## END OF THE REPORT ##\n")
        Epson.cut()

    exit()

if __name__ == "__main__":
    main()
