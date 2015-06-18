# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'

import os
import time
import re
from time import sleep

import paramiko
from jinja2 import Environment, FileSystemLoader

from sasnadmin import settings
import SASNCommands


class SASNCMDHelper(object):
    """
    This is helper for SASN command execution.
    """

    def __init__(self):
        self.rp = None
        self.test = None
        self.rsa_key_trans_done = None


    def __del__(self):
        # self.rp.close()
        self.test.close()

    def init_ssh_to_rp(self):
        """
        Creating connection towards RP card.
        :return: None
        """
        self.rp = paramiko.SSHClient()
        self.rp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.rp.connect(settings.RP_IP, username=settings.RP_USERNAME, password=settings.RP_PASSWORD)


    def init_ssh_for_test(self):
        """
        Creating connection towards host.
        :return: None
        """
        self.test = paramiko.SSHClient()
        self.test.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.test.connect(hostname=settings.HOST_IP, username=settings.HOST_USERNAME, password=settings.HOST_PASSWORD)


    def exec_cmd(self, cmd):
        """
        Execute commands in RP card and return results.
        :param cmd: Command to be executed.
        :return: execution results
        """
        stdin, stdout, stderr = self.rp.exec_command(self.__cmd_for(cmd))
        return stderr.readlines()

    def exec_cmd_test(self, cmd):
        """
        Execute commands in Host and return results.
        :param cmd: Command to be executed.
        :return: execution results
        """
        print 'command to execute', self.__cmd_for_test(cmd)
        stdin, stdout, stderr = self.test.exec_command(self.__cmd_for_test(cmd))
        stdout_info = stdout.readlines()
        if stdout_info:
            return stdout_info
        stderr_info = stderr.readlines()
        if stderr_info:
            return stderr_info

    def __cmd_for(self, cmd):
        """
        Format command line in order to be executed in RP card.
        :param cmd: Command to be executed.
        :return: None
        """
        return settings.RP_NSSH + ' "' + cmd + '"'

    def __cmd_for_test(self, cmd):
        """
        Format command line in order to be executed in Host.
        :param cmd: Command to be executed.
        :return: None
        """
        if cmd.find('\"') != -1:
            cmd = cmd.replace('"', '\\\'')
        elif cmd.find('\'') != -1:
            cmd = cmd.replace('\'', '\\\'')
        return settings.TEST_NSSH % cmd

    def get_software_information(self):
        """
        Get software information for all SASN VMs.
        :return: Software information of all SASN VMs
        format is soft_info[heuristics_release_for_vm0, vm0_heuristics_installed_for_vm0, sasn_vpf_release_for_vm0, ...]
        Every three elements are for one SASN VM.
        """
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

    def get_partition_amount(self):
        """
        Get partition amount from all appvms.
        :return: Partition amount not including partition 0
        """
        sasn_partition_info = self.exec_cmd_test(SASNCommands.SHOW_PARTITION_CONFIG)
        return max([re.search('\d+', i).group() for i in
                        [info for info in sasn_partition_info if 'ns partition set' in info]])

    def show_scm_sessions(self, partition, sasn_role):
        return self.exec_cmd_test(SASNCommands.SHOW_SCM_SESSION.format(partition, sasn_role))

    def show_status(self):
        return self.exec_cmd_test(SASNCommands.SHOW_ALL_STATUS)

    def load_apply(self, config_file):
        """
        Upload config file to RP and load apply.
        :param config_file: path of config file.
        :return: A list of info about load apply result
        """

        # generate load apply script
        load_apply_script_on_host = '/tmp/loadApply'
        config_file_on_host = config_file_on_rp = '/tmp/config.com'
        load_apply_script = self.__render_template('loadApply', config_file_on_host=config_file_on_host,
                                                   ip=settings.RP1_IP,
                                                   config_file_on_rp=config_file_on_rp)

        # put config file onto server using sftp
        self.__upload_to_host(load_apply_script, load_apply_script_on_host)
        self.__upload_to_host(config_file, config_file_on_rp)

        self.test.exec_command('chmod 744 /tmp/loadApply')
        stdin, stdout, stderr = self.test.exec_command('/tmp/loadApply')
        stdout_info = stdout.readlines()

        self.__wait_until_commit_done()

        return stdout_info[[index for index, val in enumerate(stdout_info) if val.startswith('.')][0]:-1] \
            if any([i.find('ERROR') != -1 for i in stdout_info]) else ['Configuration complete!']


    def rsa_key_trans(self):

        # app.logger.info('start trans key to RP')
        self.rsa_key_trans_done = False
        rsa_trans_script = self.__render_template('RSAKeyTrans', ip=settings.RP1_IP)
        rsa_gen_script = self.__render_template("GenerateKeys")

        self.__upload_to_host(rsa_gen_script, '/tmp/GenerateKeys')
        self.__upload_to_host(rsa_trans_script, '/tmp/RSAKeyTran')
        self.test.exec_command('chmod 744 /tmp/GenerateKeys')
        self.test.exec_command('chmod 744 /tmp/RSAKeyTran')
        stdin, stdout, stderr = self.test.exec_command('/tmp/GenerateKeys')
        # app.logger.info('stdout is: %s ', stdout.readlines())
        sleep(2)
        stdin, stdout, stderr = self.test.exec_command('/tmp/RSAKeyTran')
        # app.logger.info('stdout is: %s ', stdout.readlines())
        self.rsa_key_trans_done = True

    def check_connection(self):

        self.rsa_key_trans_done = False

        # app.logger.info('checking the connections')
        stdin, stdout, stderr = self.test.exec_command(settings.CHECK_SSH_CMD)
        # app.logger.info('try to read lines')
        result = stdout.readlines()
        resulterror = stderr.readlines()
        # app.logger.info('stdout is %s', result)
        # app.logger.info('stderr is %s', resulterror)
        # wait some time to avoid unstable situation
        time.sleep(3)
        if not result:
            print 'need to trans key!!!'
            self.rsa_key_trans()
        else:
            print 'no need to trans key!!!!'
            self.rsa_key_trans_done = True

    def cdrDecode(self, config_file):
        '''
        Upload config file to RP and decode cdr file.
        :param config_file: path of uploaded cdr file.

        '''

        self.__upload_to_host(settings.PATH_ASN1DECODER, '/tmp/asn1decoder')
        self.__upload_to_host(config_file, '/tmp/cdrfile')

        self.test.exec_command('chmod 744 /tmp/asn1decoder')
        self.test.exec_command('/tmp/asn1decoder /tmp/cdrfile')
        stdin, stdout, stderr = self.test.exec_command('cat --number /tmp/cdrfile.txt')
        return stdout.readlines()

    def check_ssh_key_ok(self):
        """
        Wait some time for ssh key trans.
        :return: True if ssh key trans is done or False
        """
        retry_wait_time = [1, 2, 3, 4, 5, 6]
        for wait_time in retry_wait_time:
            # app.logger.info('now wait: %s', wait_time)
            if self.rsa_key_trans_done:
                return True
            time.sleep(wait_time)
        return False


    def __wait_until_commit_done(self):
        """
        Check if there is still commit in progress. Checking for 15s tops.
        :return: None
        """
        retry_time = 3
        while retry_time > 0:
            info = self.exec_cmd_test(SASNCommands.SHOW_COMMIT_PROGRESS)
            if info and 'No commit in progress' in info[0]:
                return None
            retry_time -= 1
            time.sleep(5)


    def __render_template(self, template_name, **kargs):
        """
        Render template with specific parameters and save file to temp folder.
        :param template_name: Name of template file under templates folder.
        :return: Path of rendered file in temp folder.
        """
        target_file = os.path.join(settings.PROJECT_DIR, 'temp', template_name)
        j2_env = Environment(loader=FileSystemLoader(settings.PROJECT_DIR), trim_blocks=True)
        template_file = os.path.join('templates/', template_name)
        data = j2_env.get_template(template_file).render(**kargs)
        with open(target_file, 'wb') as f:
            f.write(data)
        return target_file

    def __upload_to_host(self, src_file_path, dst_file_path):
        """
        Upload specific files from local to host.
        :param src_file_path: path of source file on local machine
        :param dst_file_path: path of remote file on host
        :return: None
        """

        with self.test.open_sftp() as sftp_con:
            sftp_con.put(src_file_path, dst_file_path)


if __name__ == '__main__':
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect('10.65.100.22', username='root', password='rootroot')
    # stdin, stdout, stderr = ssh.exec_command('date')
    # print stdout.readlines()
    # print stderr.readlines()

    # test for ssh connection
    my_helper = SASNCMDHelper()
    my_helper.init_ssh_for_test()
    print my_helper.get_partition_amount()
    print my_helper.show_scm_sessions('1', 1)

    # test for template render
