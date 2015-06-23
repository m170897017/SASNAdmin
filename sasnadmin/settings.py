#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'

import os

RP_USERNAME = 'root'
RP_PASSWORD = 'root'
RP_USERNAME_ADMIN = 'admin'
RP_PASSWORD_ADMIN = 'admin'

RP_IP_DICT = {
    '1': '11.10.20.15',
    '2': '11.11.20.15',
    '3': '11.12.20.15',
    '4': '11.13.20.15',
}
# RP1_IP = '11.10.20.15'  # vm1
RP_IP = '11.13.20.15'  # vm4
# HOST_IP = '10.65.100.22'  # dell-r620-27
HOST_IP = '10.42.92.176'  # netrax3-2-95
# HOST_IP = '10.42.92.174' # netrax3-2-94
HOST_USERNAME = 'root'
HOST_PASSWORD = 'rootroot'

RP_NSSH = '/opt/disk/service-pools/sasnpool/active/bin/nssh -c'
# ssh from host to rp to execute commands
TEST_NSSH = ''.join(['ssh root@', '{0}', ' /opt/disk/service-pools/sasnpool/active/bin/nssh -c \\\"%s\\\"'])
CHECK_SSH_CMD = 'ssh root@{0} ls'
XM_LIST = 'xm list'
SASN_ROLE = {'master': '1', 'backup': '0'}

# load apply parameters
CONFIG_FILE_PATH = 'temp/config.com'
TEM_LOAD_APPLY = 'templates/loadApply'
ALLOWED_EXTENSIONS = ['wzd', 'cfg', 'conf']
MAX_CONTENT_LENGTH = 160 * 1024 * 1024

# cdr parameters

CDR_FILE_PATH = "temp/cdrfile"
SASNADMIN_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SASNADMIN_DIR)

# static file path
PATH_ASN1DECODER = os.path.join(PROJECT_DIR, 'static', 'asn1decoder')