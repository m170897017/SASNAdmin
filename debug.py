#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading

a = 1

def func_in_thread():
    print 'now in thread!!!'
    print a
    a = 2
    print a

t = threading.Thread(target=func_in_thread, args=[])
t.start()
t.join()


print 'now  print a', a
