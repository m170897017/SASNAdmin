#!/usr/bin/env python

# import paramiko
#
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect(hostname='10.65.100.22', username='root', password='rootroot')
# cmd = '''ssh root@11.13.20.15 /opt/disk/service-pools/sasnpool/active/bin/nssh -c \\"ns cluster \\'ns system show status\\' all-appvms\\"'''
# cmd1 = 'ssh root@11.13.20.15 hostname'
# stdin, stdout, stderr = ssh.exec_command(cmd)
# # print 'stdin: ', stdin.readlines()
# print 'stdout: ', stdout.readlines()
# print 'stderr: ', stderr.readlines()


def dec(func):
    print 'in dec'
    return func

def dec2(func):
    print 'in dec2'
    return func

@dec2
@dec
def test():
    print 'in test'

test()

