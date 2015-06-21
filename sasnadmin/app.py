#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Created on Nov 20, 2014

@author: eccglln
"""
from flask import Flask
from sasnadmin import settings
from logging import FileHandler, Formatter, INFO
from sasnadmin.views import admin


def create_app():

    app = Flask('SASNAdmin')

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

    app.register_blueprint(admin)

    return app
