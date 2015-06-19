#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Created on Nov 20, 2014

@author: eccglln
"""
from logging import FileHandler, Formatter, INFO
import threading

from flask import render_template, request, redirect, url_for, session, abort, Flask

from sasnadmin import settings

from sasnadmin.CMDHelper import SASNCMDHelper



app = Flask('SASNAdmin')

# configure max content length of request content
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = 'development key'

# configure app logger
file_handler = FileHandler(filename='SASNAdmin.log')
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s %(filename)s(line%(lineno)d) in function :%(funcName)s'
    '\n%(message)s'
))
file_handler.setLevel(INFO)
app.logger.addHandler(file_handler)

# init cmdhelper only for first time
# initialize SASN CMD helper
sasn_cmd_helper = SASNCMDHelper()
sasn_cmd_helper.init_ssh_for_test()
# put key trans here since we only need to do it once
rsa_key_trans_thread = threading.Thread(target=sasn_cmd_helper.check_connection, args=[])
rsa_key_trans_thread.start()



# initialization


@app.route('/my_console/', methods=['GET', 'POST'])
def search():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        session['console_output'].extend(
            ['=' * 40, '\n', 'In[%d]: ' % session['command_number'], '\n', request.form['cmd'], '\n',
             'Out[%d]: ' % session['command_number'],
             '\n', ])
        session['console_output'].extend(sasn_cmd_helper.exec_cmd_test(request.form['cmd']))
        session['command_number'] += 1
        return render_template('console.html', results=session['console_output'])
    else:
        return render_template('console.html')


@app.route('/home/')
def home():
    # app.logger.info("in home")
    if not session.get('logged_in'):
        abort(401)

    # check if connection is OK now
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


@app.errorhandler(401)
def page_need_authorization():
    return render_template('401.html'), 401


@app.route('/', methods=['GET', 'POST'])
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
        if request.form['username'] != settings.RP_USERNAME or request.form['password'] != settings.RP_PASSWORD:
            error = 'Invalid credential'
            return render_template('login.html', error=error)
        else:
            return redirect(url_for('home'))


@app.route('/logout')
def logout():
    # app.logger.info('In log out')
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/loadandapply/', methods=['GET', 'POST'])
def upload_file():

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS

    # app.logger.info('In load and apply')
    if not session.get('logged_in'):
        abort(401)
    upload_result = None
    if request.method == 'POST':
        config_file = request.files['file']
        if config_file and allowed_file(config_file.filename):
            config_file.save(settings.CONFIG_FILE_PATH)
            upload_result = sasn_cmd_helper.load_apply(settings.CONFIG_FILE_PATH)
        else:
            upload_result = ['Invalid extension of file, should end with wzd, cfg or conf']

    return render_template('loadandapply.html', upload_result=upload_result)


@app.route('/cdrDecoder/', methods=['GET', 'POST'])
def decode_CDR():
    # app.logger.info('In cdr decode')
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


@app.route('/showstatus/')
def show_status():
    # app.logger.info('In show status')
    # This is just the fake command for test, need update in the final version
    # rel_showstatus = sasn_cmd_helper.exec_cmd_test('ls')
    if not session.get('logged_in'):
        abort(401)
    rel_showstatus = sasn_cmd_helper.show_status()
    return render_template('showstatus.html', results=rel_showstatus)


@app.route('/showsessions/', methods=['GET', 'POST'])
def show_session():
    # app.logger.info('In show session')
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        # This is just the fake command for test, need update in the final version
        # session['rel_showpart'] = sasn_cmd_helper.exec_cmd_test('ls')
        # return render_template('showsessions.html', results_showpart=session['rel_showpart'])
        session['partition_amount'] = sasn_cmd_helper.get_partition_amount()
        return render_template('showsessions.html', partition_amount=session['partition_amount'])

    if request.method == 'POST':
        partition_num = request.form['partition_num']
        sasn_role = request.form['sasn_role']

        show_scm_sessions = sasn_cmd_helper.show_scm_sessions(partition_num, sasn_role)
        return render_template('showsessions.html', partition_amount=session['partition_amount'],
                               show_scm_sessions=show_scm_sessions)

@app.route('/help/', methods=['GET'])
def help():
    return render_template('help.html')

@app.route('/contact/', methods=['GET'])
def contact():
    return render_template('contact.html')

if __name__ == '__main__':

    app.run(debug=True)