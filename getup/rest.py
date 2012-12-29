#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import bottle
import config, database, http, aaa, api

app = bottle.default_app()

ALL_METHODS = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE']

@bottle.hook('before_request')
def startup():
	#print '+'*30
	app.config.user = None

@bottle.hook('after_request')
def teardown():
	app.config.user = None
	#print '-'*30

def _method(handler, *vargs, **kvargs):
	name = bottle.request.method
	if name.lower() == 'head':
		name = 'get'
	method = getattr(handler, name.lower(), None) or getattr(handler, name.upper(), None)
	if method is None:
		raise bottle.HTTPError(HTTP_METHOD_NOT_ALLOWED)
	return  method(*vargs, **kvargs)

#
# Routes
#

@bottle.route('/')
def handle_root():
	'''Root handler
	'''
	return _method(api)

@bottle.get('/admin')
@aaa.admin_user
def handle_admin():
	'''Admin area
	'''
	return _method(api.admin)

@bottle.get('/admin/status')
@aaa.admin_user
def handle_admin_status():
	'''Status
	'''
	return _method(api.admin.status)

@bottle.get('/admin/user')
@bottle.route('/admin/user/username', method=ALL_METHODS)
@aaa.admin_user
def handle_admin_user(username=None):
	'''User CRUD (admin only)
	'''
	return _method(api.admin.user, username)

@bottle.get('/user')
@bottle.get('/user/<username>')
@aaa.valid_user
def handle_user(username=None):
	'''User profile
	'''
	return _method(api.user, username=username)

@bottle.get('/user/<username>/key')
@bottle.route('/user/<username>/key/<keyname>', method=['GET', 'POST', 'DELETE'])
@bottle.route('/user/<username>/key/<keyname>/id/<keyident>', method=['GET', 'DELETE'])
@aaa.valid_user
def handle_user_key(username, keyname=None, keyident=None):
	'''User public keys
	'''
	return _method(api.user.key, username=username, keyname=keyname, keyident=keyident)

"""
@bottle.get('/app')
@bottle.route('/app/<domain_name:re:[_a-zA-Z][_0-9a-zA-Z]*>', method=ALL_METHODS)
@bottle.route('/app/<domain_name:re:[_a-zA-Z][_0-9a-zA-Z]*>/<app_name:re:[_a-zA-Z][_0-9a-zA-Z]*>', method=ALL_METHODS)
def handle_app(domain_name=None, app_name=None):
	'''Domain and App CRUD
	'''
	username = 'someone' # TODO: retrieved by auth
	if app_name is None:
		return _method(api.domain, username, domain_name)
	else:
		return _method(api.app, username, domain_name, app_name)
"""
