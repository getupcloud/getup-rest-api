#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import bottle
from bottle import HTTPError
from http import *
import app

# import api impl
import api

ALL_METHODS = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE']

def _method(handler, *vargs, **kvargs):
	name = bottle.request.method
	if name.lower() == 'head':
		name = 'get'
	method = getattr(handler, name.lower(), None) or getattr(handler, name.upper(), None)
	if method is None:
		raise HTTPError(HTTP_METHOD_NOT_ALLOWED)
	res = method(*vargs, **kvargs)
	bottle.response.status = '%i %s' % (res.status_code, res.status_message)
	return res
#
# Routes
#

@bottle.route('/')
def handle_root():
	'''Root handler
	'''
	return _method(api)

@bottle.get('/user')
@bottle.route('/user/<user_name:re:[_a-zA-Z][_0-9a-zA-Z]*>', method=ALL_METHODS)
def handle_user(user_name=None):
	'''User CRUD
	'''
	return _method(api.user, user_name)

@bottle.get('/app')
@bottle.route('/app/<domain_name:re:[_a-zA-Z][_0-9a-zA-Z]*>', method=ALL_METHODS)
@bottle.route('/app/<domain_name:re:[_a-zA-Z][_0-9a-zA-Z]*>/<app_name:re:[_a-zA-Z][_0-9a-zA-Z]*>', method=ALL_METHODS)
def handle_app(domain_name=None, app_name=None):
	'''Domain and App CRUD
	'''
	user_name = 'someone' # TODO: retrieved by auth
	if app_name is None:
		return _method(api.domain, user_name, domain_name)
	else:
		return _method(api.app, user_name, domain_name, app_name)

##############

if __name__ == '__main__':
	bottle.run(host='localhost', port=8080, debug=True, reloader=True)
