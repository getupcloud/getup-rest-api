# -*- coding: utf-8 -*-

import bottle
app = application = bottle.app()

import version
import codec
import http
import model
import config
import database
import gitlab
import response
import aaa

config.loadconfig(app)
database.start(app)

# roll the bones
import rest

##############
if __name__ == '__main__':
	bottle.run(host='localhost', port=8080, debug=True, reloader=True)
