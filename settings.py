#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'


RP_IP = '20.1.1.1'
RP_USERNAME = 'root'
RP_PASSWORD = 'root'
RP_USERNAME_ADMIN = 'admin'
RP_PASSWORD_ADMIN = 'admin'

RP_NSSH = '/opt/disk/service-pools/sasnpool/active/bin/nssh -c'
# ssh from host to rp to execute commands
TEST_NSSH = 'ssh root@11.11.20.15 /opt/disk/service-pools/sasnpool/active/bin/nssh -c \\\"%s\\\"'

RP1_IP = '11.11.20.15'  # vm2
HOST_IP = '10.65.100.22'
#HOST_IP = '10.42.92.176'  # netrax3-2-95
HOST_USERNAME = 'root'
HOST_PASSWORD = 'rootroot'

# load apply parameters
CONFIG_FILE_PATH = 'temp/config.com'
TEM_LOAD_APPLY = 'templates/loadApply'
ALLOWED_EXTENSIONS = ['wzd', 'cfg', 'conf']
MAX_CONTENT_LENGTH = 160 * 1024 * 1024

#cdr parameters

CDR_FILE_PATH = "temp/cdrfile"
