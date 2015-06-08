# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'

import os
import paramiko
from time import sleep
from jinja2 import Environment, FileSystemLoader

import settings
import SASNCommands


class SASNCMDHelper(object):
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

    def load_apply(self, config_file):
        '''
        Upload config file to RP and load apply.
        :param config_file: path of config file.
        :return: True if load apply successfully or False
        '''

        load_apply_script = self.__render_template('loadApply', ip=settings.RP1_IP, command='show card')

        # put config file onto server using sftp
        sftp_con = self.test.open_sftp()
        sftp_con.put(load_apply_script, '/tmp/loadApply')
        sftp_con.put(config_file, '/tmp/config.com')
        sftp_con.close()
        self.test.exec_command('chmod 744 /tmp/loadApply')
        stdin, stdout, stderr = self.test.exec_command('/tmp/loadApply')
        print 'stdout is: ', stdout.readlines()

        return True
        # return True if 'OK' in results else False

    def rsa_key_trans(self):
        print "start trans key to RP"
        rsa_trans_script = self.__render_template('RSAKeyTrans', ip=settings.RP1_IP)
        rsa_gen_script = self.__render_template("GenerateKeys")
        sftp_con = self.test.open_sftp()
        sftp_con.put(rsa_gen_script, '/tmp/GenerateKeys')
        sftp_con.put(rsa_trans_script, '/tmp/RSAKeyTran')
        sftp_con.close()
        self.test.exec_command('chmod 744 /tmp/GenerateKeys')
        self.test.exec_command('chmod 744 /tmp/RSAKeyTran')
        stdin, stdout, stderr = self.test.exec_command('/tmp/GenerateKeys')
        print 'stdout is: ', stdout.readlines()
        sleep (2)
        stdin, stdout, stderr = self.test.exec_command('/tmp/RSAKeyTran')
        print 'stdout is: ', stdout.readlines()

    def cdrDecode(self, config_file):
        '''
        Upload config file to RP and decode cdr file.
        :param config_file: path of uploaded cdr file.

        '''

        # put config file onto host using sftp
        sftp_con = self.test.open_sftp()
        result = sftp_con.put('static/asn1decoder', '/tmp/asn1decoder')
        print "trans decoder", result
        result = sftp_con.put(config_file, '/tmp/cdrfile')
        print "trans cdrfile", result

        sftp_con.close()
        self.test.exec_command('chmod 744 /tmp/asn1decoder')
        self.test.exec_command('/tmp/asn1decoder /tmp/cdrfile')
        stdin, stdout, stderr = self.test.exec_command('cat --number /tmp/cdrfile.txt')
        return stdout.readlines()


    def __render_template(self, template_name, **kargs):
        '''
        Render template with specific parameters and save file to temp folder.
        :param template_name: Name of template file under templates folder.
        :return: Path of rendered file in temp folder.
        '''
        cwd = os.path.dirname(os.path.abspath(__file__))
        template_file = os.path.join('templates/', template_name)
        target_file = os.path.join(cwd, 'temp', template_name)
        j2_env = Environment(loader=FileSystemLoader(cwd), trim_blocks=True)
        data = j2_env.get_template(template_file).render(**kargs)
        with open(target_file, 'wb') as f:
            f.write(data)
        return target_file


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