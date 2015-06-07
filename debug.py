# from jinja2 import Environment, FileSystemLoader
# import os
#
# cwd = os.path.dirname(os.path.abspath(__file__))
# print cwd
# j2_env = Environment(loader=FileSystemLoader(cwd), trim_blocks=True)
# path = os.path.join('templates/', 'loadApply')
# def test(**kargs):
#     # print j2_env.get_template('templates/loadApply').render(**kargs)
#     print j2_env.get_template(path).render(**kargs)
#
# test(ip='.1.', command='fffff', oo='ff')

import paramiko

if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.65.100.22', username='root', password='rootroot')
    stdin, stdout, stderr = ssh.exec_command('/tmp/loadApply')
    for i in stdout.readlines():
        print i
    print stderr.readlines()