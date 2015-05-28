#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Created on Nov 20, 2014

@author: eccglln
"""

from flask import Flask, render_template, request, redirect, url_for, session, abort

from CMDHelper import SASNCMDHelper
import settings

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = 'development key'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS


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
    if not session.get('logged_in'):
        abort(401)
    # get latest sasn status every time
    session['sasn_status'] = sasn_cmd_helper.get_software_information()
    # since we only get three kinds of info for sasn vms, we divide it by 3 in html file
    session['sasn_info_num'] = len(session['sasn_status'])
    return render_template('status.html', sasn_software_info=session['sasn_status'],
                           sasn_info_num=session['sasn_info_num'])


@app.errorhandler(401)
def page_need_authorization():
    return render_template('401.html'), 401


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != settings.RP_USERNAME or request.form['password'] != settings.RP_PASSWORD:
            error = 'Invalid credential'
        else:

            # create a ssh connection to RP card
            global sasn_cmd_helper
            sasn_cmd_helper = SASNCMDHelper()
            sasn_cmd_helper.init_ssh_for_test()

            # clear console output everytime a user is created
            session['console_output'] = []
            session['command_number'] = 0
            session['logged_in'] = True

            # clean temp dictionary according to OS
            # if os is windows
            # os.system('rm -r temp/*')

            return redirect(url_for('home'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/loadandapply/', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
        abort(401)
    error = None
    if request.method == 'POST':
        config_file = request.files['file']
        if config_file and allowed_file(config_file.filename):
            config_file.save(settings.CONFIG_FILE_PATH)
            if sasn_cmd_helper.load_apply(settings.CONFIG_FILE_PATH):
                upload_result = "Success"
            else:
                upload_result = 'Load apply failed! Please load apply again!'

            return render_template('loadandapply.html', upload_result=upload_result)
        else:
            error = 'Invalid extension of file, should end with wzd, cfg or conf'

    return render_template('loadandapply.html', error=error)


@app.route('/showstatus/')
def show_status():
    # This is just the fake command for test, need update in the final version
    # rel_showstatus = sasn_cmd_helper.exec_cmd_test('ls')
    if not session.get('logged_in'):
        abort(401)
    rel_showstatus = sasn_cmd_helper.exec_cmd_test("ns cluster 'ns system show status v' all-appvms")
    return render_template('showstatus.html', results=rel_showstatus)


@app.route('/showsessions/', methods=['GET', 'POST'])
def show_session():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        # This is just the fake command for test, need update in the final version
        session['rel_showpart'] = sasn_cmd_helper.exec_cmd_test('ls')
        return render_template('showsessions.html', results_showpart=session['rel_showpart'])

    if request.method == 'POST':
        part_select = request.form['partition']
        cmd = " ".join(['ns part set', part_select])
        show_cmd = ";".join([cmd, 'ns config scm plugin relay show session all'])
        rel_showsession = sasn_cmd_helper.exec_cmd_test(show_cmd)
        return render_template('showsessions.html', results_showpart=session['rel_showpart'],
                               results_showsess=rel_showsession)


if __name__ == '__main__':
    app.run(debug=True)