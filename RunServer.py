#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Created on Nov 20, 2014

@author: eccglln
'''
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

from werkzeug import secure_filename

from werkzeug import SharedDataMiddleware

from CMDHelper import SASNCMDHelper
import settings

UPLOAD_FOLDER = 'C:\Users\eggnzzg\SASNAdmin\static'
ALLOWED_EXTENSIONS = set(['wzd', 'cfg', 'conf'])

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        
        results = sasn_cmd_helper.exec_cmd_test(request.form['cmd'])
        
        return render_template('search.html', results=results)
    return render_template('search.html')

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != settings.RP_USERNAME or request.form['password'] != settings.RP_PASSWORD:
            error = 'Invalid credential'
        else:
            global sasn_cmd_helper
            sasn_cmd_helper = SASNCMDHelper()
            sasn_cmd_helper.init_ssh_for_test()
            return redirect(url_for('home'))

    return render_template('login.html', error=error)


@app.route('/loadandapply/', methods=['GET', 'POST'])
def upload_file():
    error = None
    upload_result = None
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            upload_result = "Success"

            return render_template('loadandapply.html', upload_result=upload_result)
        else:
            error = 'Invalid extension of file, should end with wzd, cfg or conf'

    return render_template('loadandapply.html', error=error)



if __name__ == '__main__':
     
    app.run(debug=True)