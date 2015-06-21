#!/usr/bin/env python
# -*- coding:utf-8 -*-
# from optparse import OptionParser
from sasnadmin.app import create_app

__author__ = 'eccglln'

# parse options here
# parser = OptionParser(usage='usage: %prog [options] ip', version='%prog 1.0')
# parser.add_option('-i', '--ip', help='connect to host IP, like 10.65.100.22', metavar='IP', action='store', dest='ip')
# (options, args) = parser.parse_args()


create_app().run(debug=True)
