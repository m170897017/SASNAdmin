#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Created on Nov 20, 2014

@author: eccglln
'''
from flask import Flask, render_template, request


from CMDHelper import SASNCMDHelper


app = Flask(__name__)

sasn_cmd_helper = SASNCMDHelper()
sasn_cmd_helper.init_ssh_for_test()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search', methods=[u'POST'])
def search():
    if request.method == 'POST':
        
        results = sasn_cmd_helper.exec_cmd_test(request.form['cmd'])
        
        return render_template('home.html', results=results)

if __name__ == '__main__':
     
    app.run(debug=True)