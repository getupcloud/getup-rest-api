#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
import aaa
import http
import codec
import gitlab
import provider
import projects
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
@aaa.user
@codec.parse_params('domain', 'application', 'cartridge', project='', scale=False, dev_gear=False)
def post_create(user, domain, application, project, cartridge, scale, dev_gear):
	'''Clone and bind project to application, creating any missing component.
	'''
	scale = bool(scale)
	if not project:
		project = '%s-%s' % (application, domain)

	if dev_gear:
		dev_application = 'dev%s' % application

	checklist = {
		'project': False,
		'domain': False,
		'application': False,
	}

	checklist['project'] = gitlab.Gitlab().get_project(project).status_code == 404
	checklist['domain'] = provider.OpenShift(user).get_dom(name=domain).status_code == 200
	checklist['application']  = provider.OpenShift(user).get_app(domain=domain, name=application).status_code == 404
	if dev_gear:
		checklist['dev-application']  = provider.OpenShift(user).get_app(domain=domain, name=dev_application).status_code == 404

	if checklist['project'] is False or checklist['application'] is False or \
		(dev_gear is True and checklist['dev-application'] is False):
		return response(user, status=http.HTTP_CONFLICT, body=checklist)

	p_app = projects.Application(domain=domain, name=application, cartridge=cartridge, scale=scale, \
		gear_profile=app.config.provider.openshift.gear_profile)

	if dev_gear:
		d_app = projects.Application(domain=domain, name=dev_application, cartridge=cartridge, scale=False, \
			gear_profile=app.config.provider.openshift.dev_gear_profile)
	else:
		d_app = False

	return projects.create_project(user, projects.Project(name=project, application=p_app, dev_application=d_app))

@bottle.get('/getup/rest/projects/<project>/remotes')
@aaa.user
def get_remotes(user, project):
	'''List all project remotes.
	'''
	return projects.list_remotes(user, project)

@bottle.get('/getup/rest/projects/<project>/remotes/<remote>')
@aaa.user
def get_remotes_remote(user, project, remote):
	'''Retrieve project binding.
	'''
	return projects.get_remote(user, project, remote)

@bottle.post('/getup/rest/projects/<project>/remotes')
@aaa.user
@codec.parse_params('domain', 'application')
def post_remotes(user, project, domain, application):
	'''Bind project to application.
	'''
	return projects.clone_remote(user, project, projects.Application(domain, application, None, None, None))

@bottle.delete('/getup/rest/projects/<project>/remotes/<remote>')
@aaa.user
def delete_remotes_remote(user, project, remote):
	'''Delete project binding.
	'''
	return projects.del_remote(user, project, remote)

@bottle.post('/getup/rest/projects/<project>/clone')
@aaa.user
@codec.parse_params('domain', 'application')
def post_clone(user, project, domain, application):
	'''Clone and bind project to application.
	'''
	return projects.clone_remote(user, project, projects.Application(domain, application, None, None, None))

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
def response_status_ok(func):
	def wrapper(*va, **kva):
		try:
			status = int(bottle.request.headers['X-Response-Status'])
		except (ValueError, KeyError):
			raise bottle.HTTPResponse(status=500, body='Invalid or missing header: X-Response-Status')

		if 200 <= status < 400:
			return func(*va, **kva)
		raise bottle.HTTPResponse(status=404, body='Unhandled status: %i' % status)
	return wrapper

@bottle.delete('/broker/rest/domains/<domain>')
@response_status_ok
@aaa.user
def delete_domain(user, domain):
	aaa.delete_dom(user, domain)
	return 'OK'

@bottle.post('/broker/rest/domains/<domain>/applications')
@aaa.user
def post_application(user, domain):
	params = request_params()
	# create git repo
	project = '{name}-{domain}'.format(domain=domain, **params)
	gitlab.Gitlab().add_project(project)
	# create the app
	uri = '?'.join(filter(None, [ bottle.request.fullpath, bottle.request.query_string ]))
	openshift = provider.OpenShift(user)
	res = openshift(uri).POST(verify=False, data=bottle.request.body, headers=dict(bottle.request.headers))
	# account the app
	aaa.create_app(user, domain, request_params())
	return 'OK'

@bottle.delete('/broker/rest/domains/<domain>/applications/<application>')
@response_status_ok
@aaa.user
def delete_application(user, domain, application):
	aaa.delete_app(user, domain, application)
	return 'OK'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/events')
@response_status_ok
@aaa.user
def application_events(user, domain, application):
	aaa.scale_app(user, domain, application, request_params())
	return 'OK'

@bottle.post('/broker/rest/domains/<domain>/applications/<application>/cartridges')
@response_status_ok
@aaa.user
def post_application_cartridges(user, domain, application):
	aaa.create_gear(user, domain, application, request_params())
	return 'OK'

@bottle.delete('/broker/rest/domains/<domain>/applications/<application>/cartridges/<cartridge>')
@response_status_ok
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
