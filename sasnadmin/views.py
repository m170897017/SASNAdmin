#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'eccglln'

from flask import Blueprint
from flask import render_template, request, redirect, url_for, session, abort

from sasnadmin import settings
from sasnadmin.CMDHelper import sasn_cmd_helper


admin = Blueprint("admin", __name__)


def if_ip_valid_for_ipv4(ip):
    ip = ip.split('.')
    return len(ip) == 4 and all([len(number) <= 3 and 0 < int(number) < 255 for number in ip])


@admin.route('/my_console/', methods=['GET', 'POST'])
def search():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        session['console_output'].extend(
            ['=' * 40, '\n', 'In[%d]: ' % session['command_number'], '\n', request.form['cmd'], '\n',
             'Out[%d]: ' % session['command_number'],
             '\n', ])
        session['console_output'].extend(sasn_cmd_helper.exec_cmd(request.form['cmd']))
        session['command_number'] += 1
        return render_template('console.html', results=session['console_output'])
    else:
        return render_template('console.html')


@admin.route('/home/')
def home():
    # admin.logger.info("in home")
    if not session.get('logged_in'):
        abort(401)
    sasn_cmd_helper.set_rp_ip(settings.RP_IP_DICT[session['sasn_vm']])
    sasn_cmd_helper.check_connection()
    # check if connection between host and rp is OK now
    if sasn_cmd_helper.check_ssh_key_ok():
        # get latest sasn status every time
        session['sasn_status'] = sasn_cmd_helper.get_software_information()
        # since we only get three kinds of info for sasn vms, we divide it by 3 in html file
        session['sasn_info_num'] = len(session['sasn_status'])
        return render_template('status.html', sasn_software_info=session['sasn_status'],
                               sasn_info_num=session['sasn_info_num'])
    else:
        return render_template('status.html',
                               error='There is something wrong with ssh key between RP and Host, please check!')


@admin.errorhandler(401)
def page_need_authorization():
    return render_template('401.html'), 401


@admin.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
        # clear console output everytime a user is created
        session['console_output'] = []
        session['command_number'] = 0
        session['logged_in'] = True
        session['partition_amount'] = 1

        # clean temp dictionary according to OS
        # if os is windows
        # os.system('rm -r temp/*')

        return render_template('login.html', error=error)

    if request.method == 'POST':
        # pdb.set_trace()
        if request.form.get('username'):
            # this means POST comes with username and password
            if not if_ip_valid_for_ipv4(request.form['hostip']):
                error = 'Please enter a valid IP address'
                return render_template('login.html', error=error)
            if request.form['username'] != settings.HOST_USERNAME or request.form['password'] != settings.HOST_PASSWORD:
                error = 'Invalid credential'
                # put return here since it can return immediately without doing next
                return render_template('login.html', error=error)

            if not sasn_cmd_helper.init_ssh_to_host(request.form['hostip'], request.form['username'],
                                                    request.form['password']):
                error = 'Can not log in {} with this username and password!'.format(request.form['hostip'])
                return render_template('login.html', error=error)
            else:
                sasn_vm_number = sasn_cmd_helper.get_sasn_vm_number()
                return render_template('login.html', sasn_vm_number=sasn_vm_number)
        else:
            # this means POST comes with only sasn vm number
            session['sasn_vm'] = request.form['sasn_vm']
            return redirect(url_for('admin.home'))


@admin.route('/logout')
def logout():
    # admin.logger.info('In log out')
    session.pop('logged_in', None)
    return redirect(url_for('admin.login'))


@admin.route('/loadandadminly/', methods=['GET', 'POST'])
def upload_file():
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS

    # admin.logger.info('In load and adminly')
    if not session.get('logged_in'):
        abort(401)
    upload_result = None
    if request.method == 'POST':
        config_file = request.files['file']
        if config_file and allowed_file(config_file.filename):
            config_file.save(settings.CONFIG_FILE_PATH)
            upload_result = sasn_cmd_helper.load_adminly(settings.CONFIG_FILE_PATH)
        else:
            upload_result = ['Invalid extension of file, should end with wzd, cfg or conf']

    return render_template('loadandadminly.html', upload_result=upload_result)


@admin.route('/cdrDecoder/', methods=['GET', 'POST'])
def decode_CDR():
    # admin.logger.info('In cdr decode')
    if not session.get('logged_in'):
        abort(401)
    error = None
    if request.method == 'POST':
        config_file = request.files['file']
        if config_file:
            config_file.save(settings.CDR_FILE_PATH)
            result = sasn_cmd_helper.cdrDecode(settings.CDR_FILE_PATH)
            if result != None:
                upload_result = "Success"
            else:
                upload_result = 'Decode failed'

            return render_template('cdrDecoder.html', upload_result=upload_result, result=result)

    return render_template('cdrDecoder.html', error=error)


@admin.route('/showstatus/')
def show_status():
    # admin.logger.info('In show status')
    # This is just the fake command for test, need update in the final version
    # rel_showstatus = sasn_cmd_helper.exec_cmd('ls')
    if not session.get('logged_in'):
        abort(401)
    rel_showstatus = sasn_cmd_helper.show_status()
    return render_template('showstatus.html', results=rel_showstatus)


@admin.route('/showsessions/', methods=['GET', 'POST'])
def show_session():
    # admin.logger.info('In show session')
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        # This is just the fake command for test, need update in the final version
        # session['rel_showpart'] = sasn_cmd_helper.exec_cmd('ls')
        # return render_template('showsessions.html', results_showpart=session['rel_showpart'])
        session['partition_amount'] = sasn_cmd_helper.get_partition_amount()
        return render_template('showsessions.html', partition_amount=session['partition_amount'])

    if request.method == 'POST':
        partition_num = request.form['partition_num']
        sasn_role = request.form['sasn_role']

        show_scm_sessions = sasn_cmd_helper.show_scm_sessions(partition_num, sasn_role)
        return render_template('showsessions.html', partition_amount=session['partition_amount'],
                               show_scm_sessions=show_scm_sessions)


@admin.route('/help/', methods=['GET'])
def help():
    return render_template('help.html')


@admin.route('/contact/', methods=['GET'])
def contact():
    return render_template('contact.html')