#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Created on Nov 20, 2014

@author: eccglln
'''
import os
from flask import Flask, render_template, request

from views import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search', methods=[u'POST'])
def search():
    if request.method == 'POST':
        
        files = search_path(request.form['path'])
        
        return render_template('home.html', files=files)
    
    

def search_path(path):
    
    return os.walk(path).next()[2]

if __name__ == '__main__':
     
    app.run(debug=True)