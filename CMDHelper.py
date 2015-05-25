# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'

import paramiko
import settings
import SASNCommands


class SASNCMDHelper():
    """
    This is helper for SASN command execution.
    """

    def __init__(self):
        self.rp = None
        self.test = None

    def __del__(self):
        # self.rp.close()
        self.test.close()

    def init_ssh_to_rp(self):
        '''
        Creating connection towards RP card.
        :return: None
        '''
        self.rp = paramiko.SSHClient()
        self.rp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.rp.connect(settings.RP_IP, username=settings.RP_USERNAME, password=settings.RP_PASSWORD)

    def init_ssh_for_test(self):
        '''
        Creating connection towards host.
        :return: None
        '''
        self.test = paramiko.SSHClient()
        self.test.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.test.connect(hostname=settings.HOST_IP, username=settings.HOST_USERNAME, password=settings.HOST_PASSWORD)

    def exec_cmd(self, cmd):
        '''
        Execute commands in RP card and return results.
        :param cmd: Command to be executed.
        :return: execution results
        '''
        stdin, stdout, stderr = self.rp.exec_command(self.__cmd_for(cmd))
        return stderr.readlines()

    def exec_cmd_test(self, cmd):
        '''
        Execute commands in Host and return results.
        :param cmd: Command to be executed.
        :return: execution results
        '''
        stdin, stdout, stderr = self.test.exec_command(self.__cmd_for_test(cmd))
        stdout_info = stdout.readlines()
        if stdout_info:
            return stdout_info
        stderr_info = stderr.readlines()
        if stderr_info:
            return stderr_info

    def __cmd_for(self, cmd):
        '''
        Format command line in order to be executed in RP card.
        :param cmd: Command to be executed.
        :return: None
        '''
        return settings.RP_NSSH + ' "' + cmd + '"'

    def __cmd_for_test(self, cmd):
        '''
        Format command line in order to be executed in Host.
        :param cmd: Command to be executed.
        :return: None
        '''
        if cmd.find('\"') != -1:
            cmd = cmd.replace('"', '\\\'')
        elif cmd.find('\'') != -1:
            cmd = cmd.replace('\'', '\\\'')
        return settings.TEST_NSSH % cmd

    def get_software_information(self):
        '''
        Get software information for all SASN VMs.
        :return: Software information of all SASN VMs
        format is soft_info[heuristics_release_for_vm0, vm0_heuristics_installed_for_vm0, sasn_vpf_release_for_vm0, ...]
        Every three elements are for one SASN VM.
        '''
        sasn_status = self.exec_cmd_test(SASNCommands.SHOW_SOFTWARE_INFO)
        soft_info = []
        for status_info in sasn_status:
            if 'heuristics' in status_info:
                info = status_info.split()
                soft_info.append(info[2])
                soft_info.append(' '.join(info[3:]))
            if 'sasn-vpf' in status_info:
                info = status_info.split()
                soft_info.append(info[2])
        return soft_info


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