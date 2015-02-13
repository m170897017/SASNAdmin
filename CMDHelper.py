#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'eccglln'


import paramiko
import settings

class SASNCMDHelper():
    '''
    This is helper for SASN command execution.
    '''
    def __init__(self):
        self.rp = None
        self.test = None

    def __del__(self):
        # self.rp.close()
        self.test.close()

    def init_ssh_to_rp(self):
        self.rp = paramiko.SSHClient()
        self.rp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.rp.connect(settings.RP_IP, username=settings.RP_USERNAME, password=settings.RP_PASSWORD)

    def init_ssh_for_test(self):
        self.test = paramiko.SSHClient()
        self.test.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.test.connect(hostname=settings.HOST_IP, username=settings.HOST_USERNAME, password=settings.HOST_PASSWORD)

    def exec_cmd_test(self, cmd):
        stdin, stdout, stderr = self.test.exec_command(cmd)
        return stdout.readlines()

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.rp.exec_command(self.__cmd_for(cmd))
        return stderr.readlines()

    def __cmd_for(self, cmd):
        return settings.RP_NSSH + ' "' + cmd + '"'


if __name__ == '__main__':

    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect('10.65.100.22', username='root', password='rootroot')
    # stdin, stdout, stderr = ssh.exec_command('date')
    # print stdout.readlines()
    # print stderr.readlines()

    my_helper = SASNCMDHelper()
    my_helper.exec_cmd_test('date')
    # my_helper.exec_cmd("ns cluster 'ns system show status v' all-appvms")

