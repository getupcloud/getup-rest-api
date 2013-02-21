#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
import aaa
import http
import codec
import gitlab
import provider
import project
from response import response

#class StripPathMiddleware(object):
#	def __init__(self, app):
#		self.app = app
#	def __call__(self, e, h):
#		e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
#		return self.app(e,h)
#
#app = bottle.app()
#app = StripPathMiddleware(app)

app = bottle.default_app()

def request_params():
	return bottle.request.json or bottle.request.params

#
# Binding Project <-> App
#
@bottle.post('/getup/rest/projects')
@codec.parse_params('domain', 'application', 'cartridge', project='[application]-[domain]', scale=False, app_args={})
@aaa.user
def post_create(user, domain, application, project, cartridge, scale, app_args):
	'''Clone and bind project to application, creating any missing component.
	'''
	scale = bool(scale)
	if project == '[application]-[domain]':
		project = '%s-%s' % (application, domain)

	checklist = {
		'project': False,
		'domain': False,
		'application': False,
	}

	checklist['project'] = gitlab.Gitlab().get_project(project).status_code == 404
	checklist['domain'] = provider.OpenShift(user).get_dom(name=domain).status_code == 200
	checklist['application']  = provider.OpenShift(user).get_app(domain=domain, name=application).status_code == 404

	if not checklist['project'] or not checklist['application']:
		return response(user, status=http.HTTP_CONFLICT, body=checklist)

	return project.create_project(user=user, project=project, domain=domain, application=application, cartridge=cartridge, scale=scale, **app_args)

@bottle.get('/getup/rest/projects/<project>/remotes')
@aaa.user
def get_remotes(user, project):
	'''List all project remotes.
	'''
	return project.list_remotes(user, project)

@bottle.get('/getup/rest/projects/<project>/remotes/<remote>')
@aaa.user
def get_remotes_remote(user, project, remote):
	'''Retrieve project binding.
	'''
	return project.get_remote(user, project, remote)

@bottle.post('/getup/rest/projects/<project>/remotes')
@aaa.user
def post_remotes(user, project):
	'''Bind project to application.
	'''
	domain = request_params().get('domain')
	application = request_params().get('application')
	return project.add_remote(user=user, project=project, domain=domain, application=application)

@bottle.delete('/getup/rest/projects/<project>/remotes/<remote>')
@aaa.user
def delete_remotes_remote(user, project, remote):
	'''Delete project binding.
	'''
	return project.del_remote(user, project, remote)

@bottle.post('/getup/rest/projects/<project>/clone', name='project_clone')
@aaa.user
def post_clone(user, project):
	'''Clone and bind project to application.
	'''
	domain = request_params().get('domain')
	application = request_params().get('application')
	return project.clone_remote(user=user, project=project, domain=domain, application=application)

#
# Gitlab system hooks
#
@bottle.post('/gitlab/hook')
@aaa.user
def handler_gitlab_hook():
	return 'OK'

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
	aaa.create_app(user, domain, request_params())
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
	aaa.scale_app(user, domain, application, request_params())
	return 'OK'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/cartridges')
@response_status(201)
@aaa.user
def post_application_cartridges(user, domain, application):
	aaa.create_gear(user, domain, application, request_params())
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
