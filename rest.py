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

def find_method(handler):
	name = bottle.request.method
	if name.lower() == 'head':
		name = 'get'
	method = getattr(handler, name.lower(), None) or getattr(handler, name.upper(), None)
	if method is None:
		raise HTTPError(HTTP_METHOD_NOT_ALLOWED)
	return method

#
# Routes
#

@bottle.route('/<:re:(app|a)>/<domain:re:[_a-zA-Z][_0-9a-zA-Z]+>', method=ALL_METHODS)
def handle_domain(domain):
	'''Handles domain query, creation, modification and deletion
	'''
	method = find_method(api.domain)
	return method(domain)

@bottle.route('/<:re:(app|a)>/<domain:re:[_a-zA-Z][_0-9a-zA-Z]+>/<name:re:[_a-zA-Z][_0-9a-zA-Z]+>', method=ALL_METHODS)
def handle_app(domain, name):
	'''Handles app query, creation, modification and deletion
	'''
	method = find_method(api.app)
	return method(domain, name)

@bottle.route('/<:re:(user|usr|u)>', method=ALL_METHODS)
@bottle.route('/<:re:(user|usr|u)>/<name:re:[_a-zA-Z][_0-9a-zA-Z]+>', method=ALL_METHODS)
def handle_user(name=None):
	'''Handles user query, creation, modification and deletion
	'''
	method = find_method(api.user)
	return method(name)

##############

if __name__ == '__main__':
	bottle.run(host='localhost', port=8080, debug=True, reloader=True)


'''
iaas = OpenShift('spinolacastro@gmail.com', 'kgb8y2k;.', default_domain='spinolacastro')

if 3 <= len(sys.argv) <= 4:
	print 'Creating Application:'
	try:
		name, framework, domain =  sys.argv[1:]
	except:
		name, framework =  sys.argv[1:]
		domain = None
	app = iaas.new_app(name, framework, domain)
	repo = Repo(app)
	print 'New application repo: %s' % os.path.join(os.getcwd(), repo.path)
elif len(sys.argv) == 1:
	print 'Listing Applications:'
	for app in iaas.apps():
		a = app._asdict()
		print
		print '- %(name)s (%(framework)s)' % a
		print '  url: %(url)s' % a
		print '  git: %(git_url)s' % a
	print
'''
