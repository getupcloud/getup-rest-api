# -*- coding: utf-8 -*-

import os, sys

certdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cert')
if certdir not in sys.path:
	sys.path.append(certdir)

# must be done before fist import bottle
import httplib
httplib.responses[422] = 'Unprocessable Entity'

import bottle
app = application = bottle.app()
app.catchall = True

import version
import codec
import http
import model
import config
import database
import gitlab
import response
import aaa
import provider

config.loadconfig(app)
database.start(app)

# reinstall better json plugin
bottle.uninstall(bottle.JSONPlugin)
class ExtraJSONPlugin(bottle.JSONPlugin):
	def __init__(self):
		super(ExtraJSONPlugin, self).__init__(json_dumps=codec.json_codec.encode)
bottle.install(ExtraJSONPlugin())

# roll the bones
import rest

##############
if __name__ == '__main__':
	bottle.run(host='localhost', port=8080, debug=True, reloader=True)
