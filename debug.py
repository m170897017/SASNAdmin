#!/usr/bin/env python

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='10.65.100.22', username='root', password='rootroot')
cmd = '''ssh root@11.13.20.15 /opt/disk/service-pools/sasnpool/active/bin/nssh -c \\"ns cluster \\'ns system show status\\' all-appvms\\"'''
cmd1 = 'ssh root@11.13.20.15 hostname'
stdin, stdout, stderr = ssh.exec_command(cmd)
# print 'stdin: ', stdin.readlines()
print 'stdout: ', stdout.readlines()
print 'stderr: ', stderr.readlines()