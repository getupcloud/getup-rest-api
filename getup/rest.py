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
@bottle.route('/broker/rest/domains/', method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST='create_domain', DELETE='delete_domain')
def handle_domains(**kvargs):
	'''Broker domain administration.
	Account for creating/deleting domains.
	'''
	return _method(api.broker, path=bottle.request.path)

#
# Broker aplications
#
@bottle.route('/broker/rest/domains/<domain>/applications',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/', method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST='create_app', DELETE='delete_app')
def handle_app(**kvargs):
	'''Broker application administration.
	Account for creating/deleting applications.
	'''
	return _method(api.broker, path=bottle.request.path)

def account_events(res):
	'''Callback for hook.accounting of relevant events only.
	'''
	return bottle.request.params.event in [ 'start', 'stop', 'force-stop', 'scale-up', 'scale-down' ]

@bottle.route('/broker/rest/domains/<domain>/applications/<name>/events',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/events/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST=('events_app', account_events))
def handle_events_app(**kvargs):
	'''Broker application events.
	Account for relevante events only (ex: scale-up/scale-down).
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
@hooks.accounting(POST='create_cart', DELETE='delete_cart')
def handle_cart(**kvargs):
	'''Broker cartridge administration.
	Account for creating/deleting cartridges.
	'''
	return _method(api.broker, path=bottle.request.path)

def account_cartridges(res):
	'''Callback for hook.accounting of relevant events only.
	'''
	return bottle.request.params.event in [ 'start', 'stop' ]

@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/events',  method=ALL_METHODS)
@bottle.route('/broker/rest/domains/<domain>/applications/<name>/cartridges/<cart>/events/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST=('events_cart', account_cartridges))
def handle_events_cart(**kvargs):
	'''Broker cartridge events.
	Account for relevante events only (ex: start/stop).
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
	'''Broker everything else
	'''
	return _method(api.broker, path=bottle.request.path)

#
# Gitlab projects
#
@bottle.route('/api/v2/projects',            method=ALL_METHODS)
@bottle.route('/api/v2/projects/',           method=ALL_METHODS)
@bottle.route('/api/v2/projects/<project>',  method=ALL_METHODS)
@bottle.route('/api/v2/projects/<project>/', method=ALL_METHODS)
@aaa.valid_user
@hooks.accounting(POST='create_proj', DELETE='delete_proj')
def handle_proj(project=None):
	'''Gitlab project administration.
	Account for creating/deleting projects.
	'''
	if bottle.request.method == 'POST':
		return _method(api.gitlab.projects, ath=bottle.request.path)
	elif bottle.request.method == 'DELETE':
		return _method(api.gitlab.projects, project=project, path=bottle.request.path)
	return _method(api.gitlab, path=bottle.request.path)

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
def account_users_filter(res):
	'''Callback for hooks.accouting to prevent saving any sensitive data to DB
	'''
	content = dict(filter(lambda (k,n): k != 'password', bottle.request.json.iteritems()))
	return content

@bottle.route('/api/v2/users',  method=ALL_METHODS)
@bottle.route('/api/v2/users/', method=ALL_METHODS)
@aaa.admin_user
@hooks.accounting(POST=('create_user', None, account_users_filter), DELETE='delete_user')
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
# Health check
#
@bottle.get('/health_check')
def handle_health_check():
	'''Simple healthcheck
	'''
	bottle.response.content_type = 'text/plain'
	return 'OK'
