#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading

x = 0

for i in range(10):
    if i == 1:
        print x
        x += 1
    if i > 1:
        print x

print 'end', x
