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
        self.host_ip = None
        self.rp_ip = None
        self.host = None
        self.rsa_key_trans_done = None


    def __del__(self):
        if self.host:
            self.host.close()

    def init_ssh_to_host(self, host_ip=settings.HOST_IP, username=settings.HOST_USERNAME, password=settings.HOST_PASSWORD):
        """
        Create connection towards host.
        :param host_ip: IP of host.
        :return: If connection is ok return True else return False
        """
        try:
            self.host = paramiko.SSHClient()
            self.host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.host.connect(host_ip, username=username, password=password)
        except paramiko.ssh_exception.BadAuthenticationType, e:
            # TODO: need to log e here
            return False
        # TODO: need to log something here
        return True

    def set_rp_ip(self, ip):
        """
        Set RP ip to be connected to
        :param ip: A string like '11.13.11.10'
        :return: None
        """
        self.rp_ip = ip

    def exec_cmd(self, cmd):
        """
        Execute commands in Host and return results.
        :param cmd: Command to be executed.
        :return: execution results
        """
        stdin, stdout, stderr = self.host.exec_command(self.__cmd_for_exec(cmd))
        stdout_info = stdout.readlines()
        if stdout_info:
            return stdout_info
        stderr_info = stderr.readlines()
        if stderr_info:
            return stderr_info


    def __cmd_for_exec(self, cmd):
        """
        Format command line in order to be executed in Host.
        :param cmd: Command to be executed.
        :return: None
        """
        if cmd.find('\"') != -1:
            cmd = cmd.replace('"', '\\\'')
        elif cmd.find('\'') != -1:
            cmd = cmd.replace('\'', '\\\'')
        return settings.TEST_NSSH.format(self.rp_ip) % cmd

    def get_software_information(self):
        """
        Get software information for all SASN VMs.
        :return: Software information of all SASN VMs
        format is soft_info[heuristics_release_for_vm0, vm0_heuristics_installed_for_vm0, sasn_vpf_release_for_vm0, ...]
        Every three elements are for one SASN VM.
        """
        sasn_status = self.exec_cmd(SASNCommands.SHOW_SOFTWARE_INFO)
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
        sasn_partition_info = self.exec_cmd(SASNCommands.SHOW_PARTITION_CONFIG)
        return max([re.search('\d+', i).group() for i in
                        [info for info in sasn_partition_info if 'ns partition set' in info]])

    def show_scm_sessions(self, partition, sasn_role):
        """
        Show scm session info of SASN.
        :param partition: partition number on which scm module runs
        :param sasn_role: master or backup
        :return: result info of show scm sessions
        """
        return self.exec_cmd(SASNCommands.SHOW_SCM_SESSION.format(partition, sasn_role))

    def show_status(self):
        """
        Show status of SASN VMs.
        :return: result info of show status.
        """
        return self.exec_cmd(SASNCommands.SHOW_ALL_STATUS)

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

        self.host.exec_command('chmod 744 /tmp/loadApply')
        stdin, stdout, stderr = self.host.exec_command('/tmp/loadApply')
        stdout_info = stdout.readlines()

        self.__wait_until_commit_done()

        return stdout_info[[index for index, val in enumerate(stdout_info) if val.startswith('.')][0]:-1] \
            if any([i.find('ERROR') != -1 for i in stdout_info]) else ['Configuration complete!']


    def rsa_key_trans(self):

        # app.logger.info('start trans key to RP')
        self.rsa_key_trans_done = False
        rsa_trans_script = self.__render_template('RSAKeyTrans', ip=self.rp_ip)
        rsa_gen_script = self.__render_template("GenerateKeys")

        self.__upload_to_host(rsa_gen_script, '/tmp/GenerateKeys')
        self.__upload_to_host(rsa_trans_script, '/tmp/RSAKeyTran')
        self.host.exec_command('chmod 744 /tmp/GenerateKeys')
        self.host.exec_command('chmod 744 /tmp/RSAKeyTran')
        stdin, stdout, stderr = self.host.exec_command('/tmp/GenerateKeys')
        # app.logger.info('stdout is: %s ', stdout.readlines())
        sleep(2)
        stdin, stdout, stderr = self.host.exec_command('/tmp/RSAKeyTran')
        # app.logger.info('stdout is: %s ', stdout.readlines())
        self.rsa_key_trans_done = True

    def check_connection(self):
        """
        Check connection between host and rp.
        :return: None
        """

        print 'now start to check connection'
        self.rsa_key_trans_done = False

        # app.logger.info('checking the connections')
        stdin, stdout, stderr = self.host.exec_command(settings.CHECK_SSH_CMD.format(self.rp_ip))
        # app.logger.info('try to read lines')
        result = stdout.readlines()
        resulterror = stderr.readlines()
        # app.logger.info('stdout is %s', result)
        # app.logger.info('stderr is %s', resulterror)
        # wait some time to avoid unstable situation
        time.sleep(1)
        if not result:
            self.rsa_key_trans()
        else:
            self.rsa_key_trans_done = True

    def get_sasn_vm_number(self):

        stdin, stdout, stderr = self.host.exec_command(settings.XM_LIST)
        xm_list_info = stdout.readlines()
        return len([value for value in xm_list_info if value.startswith('rp_')])


    def cdrDecode(self, config_file):
        '''
        Upload config file to RP and decode cdr file.
        :param config_file: path of uploaded cdr file.

        '''

        self.__upload_to_host(settings.PATH_ASN1DECODER, '/tmp/asn1decoder')
        self.__upload_to_host(config_file, '/tmp/cdrfile')

        self.host.exec_command('chmod 744 /tmp/asn1decoder')
        self.host.exec_command('/tmp/asn1decoder /tmp/cdrfile')
        stdin, stdout, stderr = self.host.exec_command('cat --number /tmp/cdrfile.txt')
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
            info = self.exec_cmd(SASNCommands.SHOW_COMMIT_PROGRESS)
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

        with self.host.open_sftp() as sftp_con:
            sftp_con.put(src_file_path, dst_file_path)


sasn_cmd_helper = SASNCMDHelper()

if __name__ == '__main__':
    my_helper = SASNCMDHelper()
    my_helper.init_ssh_to_host()
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect('10.65.100.22', username='root1', password='rootroot2')
    # print 'done'
    # ssh.close()
    # stdin, stdout, stderr = ssh.exec_command('date')
    # print stdout.readlines()
    # print stderr.readlines()

    # test for wrong username or password

    # assert my_helper.init_ssh_to_host('10.65.100.22', username='root', password='rootroot'), 'Can not log in host with right username/password!!'
    # assert not my_helper.init_ssh_to_host('10.65.100.22', username='root1', password='rootroot'), 'Log in host with wrong username/password'
    # assert not my_helper.init_ssh_to_host('10.65.100.22', username='root', password='rootroot1'), 'Log in host with wrong username/password'
    # print 'test for function init_ssh_to_host pass!!'

    # test for function get_sasn_vm_number
    # assert 0 <= my_helper.get_sasn_vm_number() <= 4, 'VM number of SASN should in [0, 4]'
    # print 'test for function get_sasn_vm_number pass!!'