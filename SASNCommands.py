#!/usr/bin/env python
# -*- coding:utf-8 -*-

# sasn commands executed on RP
SHOW_ALL_STATUS = 'ns cluster "ns system show status v" all-appvms'
SHOW_SOFTWARE_INFO = 'ns cluster "ns system show software information" all-appvms'
SHOW_COMMIT_PROGRESS = 'ns commit show status'
SHOW_PARTITION_CONFIG = 'ns cluster "ns partition show config" all-appvms'
SHOW_SCM_SESSION = 'ns cluster "ns partition set {0}\;ns config scm plugin relay show session all" sasnvm{1}'


