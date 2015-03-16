#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Created on Nov 20, 2014

@author: eccglln
'''
from flask import Flask, render_template, request, redirect, url_for

from CMDHelper import SASNCMDHelper
import settings


app = Flask(__name__)

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
def load():
    if request.method == 'POST':

        results = sasn_cmd_helper.exec_cmd_test(request.form['cmd'])

        return render_template('loadandapply.html', results=results)
    return render_template('loadandapply.html')

if __name__ == '__main__':
     
    app.run(debug=True)