#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'


import paramiko

class test:
    def func(self):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print 'start to connect'
        ssh.connect('10.65.100.22', username='root', password='rootroot', timeout=5)
        print 'finish connect'
        stdin, stdout, stderr = ssh.exec_command('date')

        print stdout.readlines()
        # ssh.close()

if __name__=='__main__':
    a = test()
    a.func()