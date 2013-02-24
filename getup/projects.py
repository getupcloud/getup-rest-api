# -*- coding: utf-8 -*-

import json
import bottle
import provider
import http
import gitlab
from response import response
from datetime import datetime
import collections

Application = collections.namedtuple('Application', 'domain name cartridge scale gear_profile')
Project = collections.namedtuple('Project', 'name application dev_application')

app = bottle.app()

def _cmd_list(project):
	return '%s list %s' % (app.config.webgit.remotes_bin, project)

def _cmd_create(cmd, project, name, url):
	return '%s %s %s %s "%s"' % (app.config.webgit.remotes_bin, cmd, project, name, url)

def _cmd_del(project, name):
	return '%s del %s %s' % (app.config.webgit.remotes_bin, project, name)

def run_command(user, cmd):
	try:
		cmd_result = gitlab.SSHClient().run(cmd)
		output = json.loads(cmd_result.stdout)

		if 'status' not in output:
			raise response(user, status=http.HTTP_INTERNAL_SERVER_ERROR, body="Invalid result from command: missing 'status' field")
		if 200 > output['status'] >= 400:
			raise response(user, status=output['status'], body=output.get('data'))

		return output
	except ValueError, ex:
		print 'Failure parsing command output: %s' % ex
		raise response(user, status=http.HTTP_INTERNAL_SERVER_ERROR, body=str(ex))
	except Exception, ex:
		print "Failure executing command: '%s' with status=%i" % (cmd, cmd_result.retcode)
		print '--- stdout'
		print cmd_result.stdout
		print '--- stderr'
		print cmd_result.stderr
		print '---'
		raise response(user, status=http.HTTP_INTERNAL_SERVER_ERROR, body=str(ex))

def _get_remotes(user, project):
	# garantee ownership
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		raise response(user, res)

	return run_command(user, _cmd_list(project))

def list_remotes(user, project):
	if not all([user, project]):
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	remotes = _get_remotes(user, project)
	return response(user, status=remotes['status'], body=remotes)

def get_remote(user, project, remote):
	if not all([user, project, remote]):
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	remotes = _get_remotes(user, project)
	rem = filter(lambda r: r['name'] == remote, remotes['remotes'])
	if not rem:
		return response(user, status=http.HTTP_NOT_FOUND)
	res = { 'project': project }
	res.update(rem[0])
	return response(user, status=http.HTTP_OK, body=res)

def _create_remote(user, project, domain, application, command='add'):
	if not all([user, project, domain, application]):
		raise response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	# retrieve openshift app
	res = provider.OpenShift(user).get_app(domain=domain, name=application)
	if not res.ok:
		raise response(user, res)
	app_data = res.json['data']

	# retrieve gitlab project
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		raise response(user, res)

	remote = '%(name)s-%(domain_id)s' % app_data
	return run_command(user, _cmd_create(command, project, remote, app_data['git_url']))

def _install_getup_key(user):
	try:
		with open(app.config.webgit.pubkey_file) as fp:
			prov = provider.OpenShift(user)
			for i, key in enumerate(filter(lambda l: l.split(), fp.readlines())):
				if key[0].startswith('#'):
					continue
				type, content, name = key.split()[:2] + [ 'getupcloud%i' % i ]
				res = prov.add_key(name=name, content=content, type=type)
				if res.status_code not in [ http.HTTP_CREATED, http.HTTP_CONFLICT ]:
					print 'WARNING: error posting getup pub-key (%s/%s) to user %s: %s %s' % (type, name, user['email'], res.status_code, res.reason)
				print 'installed getup pub-key: %s/%s %s...%s' % (type, name, content[:6], content[-6:])
	except Exception, ex:
		print 'WARNING: unable to install getup pub-key to user %s: %s: %s' % (user['email'], ex.__class__, ex)

def clone_remote(user, project_name, application):
	_install_getup_key(user)
	res = _create_remote(user, project_name, application.domain, application.name, 'clone')
	return response(user, status=res['status'], body=res)

def add_remote(user, project, domain, application):
	_install_getup_key(user)
	res = _create_remote(user, project, domain, application, 'add')
	return response(user, status=res['status'], body=res)

def del_remote(user, project, remote):
	if not all([user, project, remote]):
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	# retrieve gitlab project
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		return response(user, res)

	result = run_command(user, _cmd_del(project, remote))
	return response(user, status=result['status'], body=result)

def _create_domain(user, app):
	res = provider.OpenShift(user).get_dom(app.domain)
	if res.ok:
		return None

	res = provider.OpenShift(user).add_dom(app.domain)
	if res.ok:
		print 'Domain created:', app.domain
		return res

	raise response(user, status=res.status_code, body=res.json)

def _create_gitlab_project(user, proj):
	res = gitlab.Gitlab().add_project(name=proj.name)
	if res.ok:
		print 'Project created:', proj.name
		return res

	raise response(user, status=res.status_code, body=res.json)

def _create_application(user, app):
	res = provider.OpenShift(user).add_app(**app._asdict())
	if res.ok:
		print 'Application created: %s-%s' % (app.name, app.domain)
		return res

	raise response(user, status=res.status_code, body=res.json)

def create_project(user, project):
	start_time = datetime.utcnow().ctime()

	report = []
	def add_report(action, description, **kva):
		r = { 'action': action, 'description': description }
		if 'res' in kva:
			r.update(status=res.status_code, content=res.json)
			kva.pop('res')
		r.update(kva)
		report.append(r)

	# create openshift domain
	_create_domain(user, project.application)

	# create gitlab project
	res = _create_gitlab_project(user, project)
	add_report('project', 'Create fresh project repository', res=res)

	# create openshift app
	res = _create_application(user, project.application)
	add_report('application', 'Create fresh openshift application', res=res)

	# create dev openshift app is applicable
	if project.dev_application:
		_create_application(user, project.dev_application)
		add_report('dev_application', 'Create fresh openshift dev_application', res=res)

	# clone and setup default remote
	res = clone_remote(user, project.name, project.application)
	add_report('clone', 'Clone and setup application code into project repository', res=res)
	if not res.ok:
		res.body = report
		raise res
	print 'Project cloned from application: %s-%s -> %s' % (project.application.name, project.application.domain, project.name)

	add_report('finish', 'All operations sucessfully finished', start_time=start_time, end_time=datetime.utcnow().ctime())
	return response(user, status=http.HTTP_CREATED, body=report)
