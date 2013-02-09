#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, logging
import bottle
import config, database, http
import aaa, api, response

app = bottle.default_app()

ALL_METHODS = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE']

@bottle.hook('before_request')
def startup():
	app.config.user = None
	bottle.response.headers['Cache-Control'] = 'no-cache'
	#print time.time(),'-', bottle.request.method, bottle.request.path

@bottle.hook('after_request')
def teardown():
	app.config.user = None
	#print time.time(),'-', bottle.response.status_code

def _method(handler, *vargs, **kvargs):
	name = bottle.request.method
	if name.lower() == 'head':
		name = 'get'
	method = getattr(handler, name.lower(), None) or getattr(handler, name.upper(), None)
	if method is None:
		raise response.ResponseMethodNotAllowed()
	return method(*vargs, **kvargs)

#
# Main entry point
#
#TODO: return subsystems entry points
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
# Broker domains
#
@bottle.route('/broker/rest/domains',  method=ALL_METHODS)
@aaa.valid_user
def handle_domains(**kvargs):
	'''Broker domains administration.
	'''
	if bottle.request.method.upper() == 'POST':
		return _method(api.broker.domain, path=bottle.request.path)
	else:
		return _method(api.broker, path=bottle.request.path)

@bottle.route('/broker/rest/domains/<domain>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/', method=ALL_METHODS)
@aaa.valid_user
def handle_domain(**kvargs):
	'''Broker domain administration.
	'''
	return _method(api.broker.domain, path=bottle.request.path)

##TODO: account
#
# Broker aplications
#
@bottle.route('/broker/rest/domains/<domain>/applications',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/', method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/', method=ALL_METHODS)
@aaa.valid_user
def handle_app(**kvargs):
	'''Broker application administration.
	'''
	if bottle.request.method.upper() == 'POST'
		return _method(api.broker.app, path=bottle.request.path)
	elif bottle.request.method.upper() == 'DELETE':
		return _method(api.broker.app, path=bottle.request.path, domain_id=kvargs['domain'], app_name=kvargs['name'])
	else:
		return _method(api.broker, path=bottle.request.path)

##TODO: account
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/events',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/events/', method=ALL_METHODS)
@aaa.valid_user
def handle_events_app(**kvargs):
	'''Broker application events.
	'''
	return _method(api.broker, path=bottle.request.path)

#
# Broker cartridges
#
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/', method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/', method=ALL_METHODS)
@aaa.valid_user
def handle_cart(**kvargs):
	'''Broker cartridge administration.
	'''
	return _method(api.broker, path=bottle.request.path)

@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/events',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/events/', method=ALL_METHODS)
@aaa.valid_user
def handle_events_cart(**kvargs):
	'''Broker cartridge events.
	'''
	return _method(api.broker, path=bottle.request.path)

#
# Broker user keys
#
@bottle.route('/broker/rest/user/keys',          method=ALL_METHODS)
@bottle.route('/broker/rest/user/keys/',         method=ALL_METHODS)
@bottle.route('/broker/rest/user/keys/<keyname>',   method=ALL_METHODS)
@bottle.route('/broker/rest/user/keys/<keyname>/',  method=ALL_METHODS)
@aaa.valid_user
def handle_broker_keys(keyname=None):
	'''Broker keys administration.
	Garantees a single key to spread to all backends.
	'''
	if bottle.request.method.upper() == 'POST':
		return _method(api.broker.keys, path=bottle.request.path)
	elif bottle.request.method.upper() in [ 'PUT', 'DELETE' ]:
		return _method(api.broker.keys, keyname=keyname, path=bottle.request.path)
	else:
		return _method(api.broker, path=bottle.request.path)

#
# Broker passthru
#
@bottle.route('/broker/<path:path>', method=ALL_METHODS)
@aaa.valid_user
def handle_broker(path=None):
	'''Broker everything else
	'''
	return _method(api.broker, path=bottle.request.path)

#
# Gitlab current user
#
@bottle.route('/api/v2/user',               method=ALL_METHODS)
@bottle.route('/api/v2/user/',              method=ALL_METHODS)
@bottle.route('/api/v2/user/keys/',         method=ALL_METHODS)
@bottle.route('/api/v2/user/keys',          method=ALL_METHODS)
@bottle.route('/api/v2/user/keys/<keyid>',  method=ALL_METHODS)
@bottle.route('/api/v2/user/keys/<keyid>/', method=ALL_METHODS)
@aaa.valid_user
def handle_user(keyid=None):
	'''Gitlab user (owner) administration
	Garantees a single key to spread to all backends.
	'''
	if keyid is not None:
		return _method(api.gitlab.user, keyid=keyid, path=bottle.request.path)
	else:
		return _method(api.gitlab.user, path=bottle.request.path)

#
# Gitlab users admin
#
@bottle.route('/api/v2/users',  method=ALL_METHODS)
@bottle.route('/api/v2/users/', method=ALL_METHODS)
@aaa.admin_user
def handle_current_user():
	'''Gitlab current user administration
	'''
	return _method(api.gitlab.users, path=bottle.request.path)

@bottle.route('/api/v2/users/<name>',  method=ALL_METHODS)
@bottle.route('/api/v2/users/<name>/', method=ALL_METHODS)
@aaa.admin_user
def handle_user(name):
	'''Gitlab user administration
	'''
	return _method(api.gitlab.users, name=name, path='/api/v2/users', userid=name)

#
# Gitlab user session
#
@bottle.route('/api/v2/session', method=ALL_METHODS)
def handle_user(**kvargs):
	'''Gitlab user session (auth via password, not token)
	'''
	return _method(api.gitlab.session)

#
# Gitlab passthru
#
@bottle.route('/api/v2/<path:path>', method=ALL_METHODS)
@aaa.valid_user
def handle_user(**kvargs):
	'''Gitlab everything else
	'''
	return _method(api.gitlab, path=bottle.request.path)

#
# Gitlab system hooks
#
@bottle.post('/gitlab/hook')
@aaa.admin_user
def handle_gitlab_hook():
	'''Handler for gitlab system hooks
	'''
	return _method(api.gitlab.hook)

#
# Binding Project <-> App
#
@bottle.route('/bindings/domains/<domain>/applications/<name>/projects', method=ALL_METHODS)
@aaa.valid_user
def handle_targets(domain, name):
	'''
	'''
	return _method(api.bindings, domain=domain, name=name)

#
# Accouting
#
@bottle.post('/accounting/<username>')
@aaa.admin_user
def handle_accounting(username):
	'''Accouting created gear.
	'''
	return _method(api.acct, username=username)

@bottle.delete('/accounting/<username>/<appname>')
@aaa.admin_user
def handle_accounting(username, appname):
	'''Accouting deleted gear.
	'''
	return _method(api.acct, username=username, appname=appname)

#
# Health check
#
@bottle.get('/health_check')
def handle_health_check():
	'''Simple healthcheck
	'''
	bottle.response.content_type = 'text/plain'
	return 'OK'
