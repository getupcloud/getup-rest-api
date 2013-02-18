#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
import aaa
import bindings

app = bottle.default_app()

#
# Binding Project <-> App
#
@bottle.get('/getup/rest/projects/<project>/remotes')
@aaa.user
def handle_bindings(user, project):
	'''List all project bindings.
	'''
	return bindings.list_remotes(user, project)

@bottle.get('/getup/rest/projects/<project>/remotes/<remote>')
@aaa.user
def handle_bindings(user, project, remote):
	'''Retrieve project binding.
	'''
	return bindings.get_remote(user, project, remote)

@bottle.post('/getup/rest/projects/<project>/remotes')
@aaa.user
def handle_bindings(user, project):
	'''Bind project to application.
	'''
	domain = bottle.request.params.get('domain')
	application = bottle.request.params.get('application')
	return bindings.add_remote(user=user, project=project, domain=domain, application=application)

@bottle.delete('/getup/rest/projects/<project>/remotes/<remote>')
@aaa.user
def handle_bindings(user, project, remote):
	'''Delete project binding.
	'''
	return bindings.del_remote(user, project, remote)

#
# Broker callbacks
#
def response_status(*statuses):
	class ResponseStatusDecorator:
		def __init__(self, func):
			self.statuses = statuses
			self.func = func
		def __call__(self, *va, **kva):
			try:
				status = int(bottle.request.headers['X-Response-Status'])
			except (ValueError, KeyError):
				raise bottle.HTTPResponse(status=500, body='Invalid or missing header: X-Response-Status')

			if status not in self.statuses:
				raise bottle.HTTPResponse(status=404, body='Unhandled status: %i' % status)
			return self.func(*va, **kva)
	return ResponseStatusDecorator

@bottle.post('/broker/rest/domains/<domain>/applications')
@response_status(201)
@aaa.user
def post_application(user, domain):
	aaa.create_app(user, bottle.request.params)
	return 'OK'

@bottle.delete('/broker/rest/domains/<domain>/applications/<application>')
@response_status(204)
@aaa.user
def delete_application(user, domain, application):
	aaa.delete_app(user, domain, application)
	return 'OK'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/events')
@response_status(200)
@aaa.user
def application_events(user, domain, application):
	aaa.scale_app(user, domain, application, bottle.request.params)
	return 'OK'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/cartridges')
@response_status(201)
@aaa.user
def post_application_cartridges(user, domain, application):
	aaa.create_gear(user, domain, application, bottle.request.params)
	return 'OK'

@bottle.delete('/broker/rest/domains/<domain>/applications/<application>/cartridges/<cartridge>')
@response_status(200)
@aaa.user
def delete_application_cartridges(user, domain, application, cartridge):
	aaa.delete_gear(user, domain, application, cartridge)
	return 'OK'

#
# Health check
#
@bottle.get('/health_check')
def handle_health_check():
	'''Simple health check
	'''
	if 'X-Response-Status' in bottle.request.headers:
		print '%s: X-Response-Status: %s' % (bottle.request.path, bottle.request.headers['X-Response-Status'])
	bottle.response.content_type = 'text/plain'
	return 'OK\n'
