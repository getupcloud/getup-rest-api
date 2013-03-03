#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import aaa
import http
import json
import codec
import bottle
import gitlab
import provider
import projects
from response import response, to_bottle_response

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

def request_params(name=None):
	if name:
		return bottle.request.json.get(name) if bottle.request.json else bottle.request.params.get(name)
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
		gear_profile=app.config.provider.openshift.default_gear_profile)

	if dev_gear:
		d_app = projects.Application(domain=domain, name=dev_application, cartridge=cartridge, scale=False, \
			gear_profile=app.config.provider.openshift.devel_gear_profile)
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
	headers = bottle.HeaderDict(bottle.request.headers)
	headers.pop('content-length', None)
	body = request_params()

	#TODO: fix default gear_profile on broker
	if 'gear_profile' not in body:
		body.update(gear_profile=app.config.provider.openshift.default_gear_profile)

	is_dev_gear = body['gear_profile'] == app.config.provider.openshift.devel_gear_profile
	name = body['name']
	project = '{name}-{domain}'.format(name=name, domain=domain)

	# For dev gears, the project already exists.
	# We simply add the new app as a remote to the project.
	# The project name is extracted from :initial_git_url, given
	# as a parameter to this request.
	# The git url MUST be inside our domain (ex: git@git.getupcloud.com/<project>.git)
	if is_dev_gear and 'initial_git_url' in body:
		match = re.match('(?:[a-z]+://)?git@git\.getupcloud\.com/(?P<project>[^.]+)\.git$', body['initial_git_url'], re.IGNORECASE)
		if not match:
			raise bottle.HTTPError(status=500, body='invalid git repository: {repo}'.format(repo=body['initial_git_url']))
		project = match.group('project')
		body.pop('initial_git_url', None)

	print 'Creatin application:'
	print ' - user:      {user.email}'.format(user=user)
	print ' - name:      {name}'.format(name=name)
	print ' - domain:    {domain}'.format(domain=domain)
	print ' - project:   {project}'.format(project=project)
	print ' - gear:      {body[gear_profile]}'.format(body=body)

	# create git repo
	if not is_dev_gear:
		gitlab.Gitlab().add_project(project)

	# create the app
	print 'creating application: name={project}'.format(project=project)
	openshift = provider.OpenShift(user, hostname=app.config.provider.openshift.ops_hostname)
	uri = '?'.join(filter(None, [ bottle.request.fullpath, bottle.request.query_string ]))

	if bottle.request.json:
		body = json.dumps(body)

	os_res = openshift(uri).POST(verify=False, data=body, headers=headers)
	print 'creating application: name={project} (done with {status})'.format(project=project, status=os_res.status_code)
	if not os_res.ok:
		print 'ERROR:', os_res.text
		return to_bottle_response(os_res)

	if is_dev_gear:
		res = projects.add_remote(user, project, projects.Application(domain, project, None, None, None))
	else:
		res = projects.clone_remote(user, project, projects.Application(domain, name, None, None, None))

	if not res.ok:
		print 'ERROR:', res.body

	# account the app
	print 'accounting new application: name={project}'.format(project=project)
	aaa.create_app(user, domain, request_params())

	return to_bottle_response(os_res)

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
