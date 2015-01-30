#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired & adopted from http://graphicdesign.stackexchange.com/questions/27300/export-photoshop-swatch-sheet-to-a-human-readable-document

import struct
import sys
import csv
import os

class ColorSwatch(list):
    def __init__(self, fp):
        self.rawdata  = struct.unpack(">5H",fp.read(10))
        namelen, = struct.unpack(">I",fp.read(4))
        cp = fp.read(2*namelen)
        self.name = cp[0:-2].decode('utf-16-be')
        self.typename = self.colorTypeName()


    def colorTypeName(self):
        try:
            return {0:"RGB", 1:"HSB",
                    2:"CMYK",7:"Lab",
                    8:"Grayscale"}[self.rawdata[0]]
        except IndexError:
            print self.rawdata[0]

    def __strCMYK(self):
        rgb8bit = map(lambda a: (65535 - a)/655.35, self.rawdata[1:])
        return "{name},{typename},{0},{1},{2},{3}".format(*rgb8bit,**self.__dict__)

    def __strRGB(self):
        # rgb8bit = map(lambda a: a/256,self.rawdata[1:4])
        # (r, g, b) = (self.rawdata[1],self.rawdata[2]/256,self.rawdata[3]/256)
        return "{name},{typename},{0},{1},{2}".format(self.rawdata[1],self.rawdata[2],self.rawdata[3],**self.__dict__)

    def __strGrayscale(self):
        gray = self.rawdata[1]/100.
        return "{name},{typename},{0}".format(gray,**self.__dict__)

    def __strLab(self):
        data = str(self.rawdata)
        return "{name},{typename},{0}".format(','.join(data.split(',')[1:-1]),**self.__dict__)

    def __str__(self):
        return {0: self.__strRGB, 1:"HSB",
                2:self.__strCMYK,7:self.__strLab,
                8:self.__strGrayscale}[self.rawdata[0]]()

with open(os.path.realpath(sys.argv[1]), "rb") as acoFile:
    #skip ver 1 file
    head = acoFile.read(2)
    ver, = struct.unpack(">H",head)
    if (ver != 1):
        raise TypeError("Probably not a adobe aco file")
    count = acoFile.read(2)
    cnt, = struct.unpack(">H",count)
    acoFile.seek(cnt*10,1)

    #read ver2 file
    head = acoFile.read(2)
    ver, = struct.unpack(">H",head)
    if (ver != 2):
        raise TypeError("Probably not a adobe aco file")
    count = acoFile.read(2)
    count, = struct.unpack(">H",count)

    with open(os.path.join(sys.argv[2], 'swatchpng.csv'), "w+") as datafile:
        datacsv = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for _ in range(count):
            s = str(ColorSwatch(acoFile))
            datacsv.writerow(s.split(','))
        