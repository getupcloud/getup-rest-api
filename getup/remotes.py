# -*- coding: utf-8 -*-

import json
import bottle
import provider
import http
import gitlab
from response import response

app = bottle.app()

def _cmd_list(project):
	return '%s list %s' % (app.config.webgit['remotes_bin'], project)

def _cmd_create(cmd, project, name, url):
	return '%s %s %s %s "%s"' % (app.config.webgit['remotes_bin'], cmd, project, name, url)

def _cmd_del(project, name):
	return '%s del %s %s' % (app.config.webgit['remotes_bin'], project, name)

def _get_remotes(user, project):
	# garantee ownership
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		raise response(user, res)

	cmd = _cmd_list(project)
	return json.loads(run_command(user, cmd).stdout)

def list_remotes(user, project):
	if not all([user, project]):
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	remotes = _get_remotes(user, project)
	return response(user, status=http.HTTP_OK, body=remotes)

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
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	# retrieve openshift app
	res = provider.OpenShift(user).get_app(domain=domain, name=application)
	if not res.ok:
		return response(user, res)
	app_data = res.json['data']

	# retrieve gitlab project
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		return response(user, res)

	remote = '%(name)s-%(domain_id)s' % app_data
	cmd = _cmd_create(command, project, remote, app_data['git_url'])
	result = run_command(user, command)
	return response(user, status=http.HTTP_CREATED, body=json.loads(result.stdout))

def add_remote(user, project, domain, application):
	return _create_remote(user, project, domain, application, 'add')

def clone_remote(user, project, domain, application):
	return _create_remote(user, project, domain, application, 'clone')

def del_remote(user, project, remote):
	if not all([user, project, remote]):
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	# retrieve gitlab project
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		return response(user, res)

	cmd = _cmd_del(project, remote)
	result = run_command(user, cmd)
	return response(user, status=http.HTTP_NO_CONTENT)

def run_command(user, cmd):
	try:
		ret = gitlab.SSHClient().run(cmd)
		if ret.returncode != 0:
			raise Exception({'stdout': ret.stdout, 'stderr': ret.stderr, 'status': ret.returncode})
		return ret # json.loads(ret.stdout)
	except Exception, ex:
		raise response(user, status=http.HTTP_INTERNAL_SERVER_ERROR, body=str(ex))

