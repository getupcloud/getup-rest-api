#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
import database, http
import aaa

app = bottle.default_app()

#
# Binding Project <-> App
#
#@bottle.route('/bindings/domains/<domain>/applications/<name>/projects', method=ALL_METHODS)
#@aaa.user
#def handle_targets(user, domain, name):
#	'''
#	'''
#	return _(api.bindings, domain=domain, name=name)

#
# Health check
#
@bottle.get('/health_check')
def handle_health_check():
	'''Simple healthcheck
	'''
	bottle.response.content_type = 'text/plain'
	return 'OK\n'

#
# Broker callbacks
#
def response_status(*statuses):
	class ResponseStatusDecorator:
		def __init__(self, func):
			self.statuses = statuses
			self.func = func
		def __call__(self, *va, **kva):
			status = int(bottle.request.headers['X-Response-Status'])
			if status not in self.statuses:
				raise bottle.HTTPResponse(status=404, body='Unhandled status: %i' % status)
			return self.func(*va, **kva)
	return ResponseStatusDecorator

@bottle.post('/broker/rest/domains/<domain>/applications')
@response_status(201)
@aaa.user
def post_application(user, domain):
	aaa.create_app(user, bottle.request.params)
	return 'ok'

@bottle.delete('/broker/rest/domains/<domain>/applications/<application>')
@response_status(204)
@aaa.user
def delete_application(user, domain, application):
	aaa.delete_app(user, domain, application)
	return 'ok'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/events')
@response_status(200)
@aaa.user
def application_events(user, domain, application):
	aaa.scale_app(user, domain, application, bottle.request.params)
	return 'ok'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/cartridges')
@response_status(201)
@aaa.user
def post_application_cartridges(user, domain, application):
	aaa.create_gear(user, domain, application, bottle.request.params)
	return 'ok'

@bottle.delete('/broker/rest/domains/<domain>/applications/<application>/cartridges/<cartridge>')
@response_status(204)
@aaa.user
def delete_application_cartridges(user, domain, application, cartridge):
	aaa.delete_gear(user, domain, application, cartridge)
	return 'ok'

#if __name__ == '__main__':
#	bottle.run(host='0.0.0.0', port=8011, debug=True, reloader=True)
