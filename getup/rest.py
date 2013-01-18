#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, logging
import bottle
import config, database, http
import hooks, aaa, api, response

app = bottle.default_app()

ALL_METHODS = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE']

@bottle.hook('before_request')
def startup():
	app.config.user = None
	bottle.response.headers['Cache-Control'] = 'no-cache'
	print time.time(),'-', bottle.request.method, bottle.request.path

@bottle.hook('after_request')
def teardown():
	app.config.user = None
	print time.time(),'-', bottle.response.status_code

def _method(handler, *vargs, **kvargs):
	name = bottle.request.method
	if name.lower() == 'head':
		name = 'get'
	method = getattr(handler, name.lower(), None) or getattr(handler, name.upper(), None)
	if method is None:
		raise response.ResponseMethodNotAllowed()
	return method(*vargs, **kvargs)

#
# Routes
#

@bottle.route('/')
def handle_root():
	'''Root handler
	'''
	return _method(api)

@bottle.get('/status')
@aaa.admin_user
def handle_status():
	'''System status and config
	'''
	return _method(api.status)

#
# Domains
#
@bottle.route('/broker/rest/domains',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST='create_domain')
def handle_domains(**kvargs):
	return _method(api.broker, path=bottle.request.path)

@bottle.route('/broker/rest/domains/<domain>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(DELETE='delete_domain')
def handle_domain(**kvargs):
	return _method(api.broker, path=bottle.request.path)

#
# Aplications
#
@bottle.route('/broker/rest/domains/<domain>/applications',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/', method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST='create_app', DELETE='delete_app')
def handle_app(**kvargs):
	return _method(api.broker, path=bottle.request.path)

def account_events(res):
	return bottle.request.params.event in [ 'start', 'stop', 'force-stop', 'scale-up', 'scale-down' ]

@bottle.route('/broker/rest/domains/<domain>/applications/<name>/events',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/events/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST=('events_app', account_events))
def handle_events_app(**kvargs):
	return _method(api.broker, path=bottle.request.path)

#
# Cartridges
#
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/', method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST='create_cart', DELETE='delete_cart')
def handle_cart(**kvargs):
	return _method(api.broker, path=bottle.request.path)

def account_cartridges(res):
	return bottle.request.params.event in [ 'start', 'stop' ]

@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/events',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/events/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST=('events_cart', account_cartridges))
def handle_events_cart(**kvargs):
	return _method(api.broker, path=bottle.request.path)

@bottle.route('/broker/rest/user/keys',          method=ALL_METHODS)
@bottle.route('/broker/rest/user/keys/',         method=ALL_METHODS)
@bottle.route('/broker/rest/user/keys/<keyname>',   method=ALL_METHODS)
@bottle.route('/broker/rest/user/keys/<keyname>/',  method=ALL_METHODS)
@aaa.valid_user
def handle_broker_keys(keyname=None):
	if bottle.request.method == 'POST':
		return _method(api.broker.keys, path=bottle.request.path)
	elif bottle.request.method in [ 'PUT', 'DELETE' ]:
		return _method(api.broker.keys, keyname=keyname, path=bottle.request.path)
	else:
		return _method(api.broker, path=bottle.request.path)

#
# Broker passthru
#
@bottle.route('/broker/rest/<path:path>')
@aaa.valid_user
def handle_broker(path=None):
	return _method(api.broker, path=path)

#
# Single user
#
@bottle.route('/api/v2/user',             method=ALL_METHODS)
@bottle.route('/api/v2/user/',            method=ALL_METHODS)
@bottle.route('/api/v2/user/keys/',       method=ALL_METHODS)
@bottle.route('/api/v2/user/keys',        method=ALL_METHODS)
@bottle.route('/api/v2/user/keys/<key>',  method=ALL_METHODS)
@bottle.route('/api/v2/user/keys/<key>/', method=ALL_METHODS)
@aaa.valid_user
def handle_user(key=None):
	'''User profile
	'''
	return _method(api.user, path=bottle.request.path)

#
# Users admin
#
def account_users_filter(res):
	content = dict(filter(lambda (k,n): k != 'password', bottle.request.json.iteritems()))
	return content

@bottle.route('/api/v2/users',  method=ALL_METHODS)
@bottle.route('/api/v2/users/', method=ALL_METHODS)
@aaa.admin_user
@hooks.accounting(POST=('create_user', None, account_users_filter), DELETE='delete_user')
def handle_user():
	'''User profile
	'''
	return _method(api.users, path=bottle.request.path)

@bottle.route('/api/v2/users/<name>',  method=ALL_METHODS)
@bottle.route('/api/v2/users/<name>/', method=ALL_METHODS)
@aaa.admin_user
def handle_user(name):
	'''User profile
	'''
	return _method(api.users, name=name, path='/api/v2/users', userid=name)

#
# Gitlab system hooks
#
@bottle.post('/gitlab/hook')
@aaa.admin_user
def handle_gitlab_hook():
	return _method(api.gitlab)

#
# Health check
#
@bottle.get('/health_check')
def handle_health_check():
	bottle.response.content_type = 'text/plain'
	return 'OK'
