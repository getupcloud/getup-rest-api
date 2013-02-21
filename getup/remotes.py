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

def run_command(user, cmd):
	def parse_command_result(res):
		try:
			ns = {}
			exec 'output=%s' % res.stdout in ns
			output = ns['output']
		except:
			print "Unexpected result from command: type=%s (%s)" % (type(res.stdout), cmd)
			print '--- stdout'
			print res.stdout
			print '--- stderr'
			print res.stderr
			print '--- status: %i' % res.returncode;
			raise Exception("Unexpected result from command: type=%s (%s)" % (type(res.stdout), cmd))
		if 'status' not in output:
			raise Exception("Invalid result from command: missing 'status' field")
		return output

	try:
		result = parse_command_result(gitlab.SSHClient().run(cmd))
		if 200 > result['status'] >= 400:
			raise response(user, status=result['status'], body=result['data'])
		return result
	except Exception, ex:
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
	result = run_command(user, _cmd_create(command, project, remote, app_data['git_url']))
	return response(user, status=http.HTTP_CREATED, body=result)

def _install_getup_key(user):
	try:
		with open(app.config.webgit['pubkey_file']) as fp:
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

def clone_remote(user, project, domain, application):
	_install_getup_key(user)
	return _create_remote(user, project, domain, application, 'clone')

def add_remote(user, project, domain, application):
	_install_getup_key(user)
	return _create_remote(user, project, domain, application, 'add')

def del_remote(user, project, remote):
	if not all([user, project, remote]):
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	# retrieve gitlab project
	res = gitlab.Gitlab().get_project(project)
	if not res.ok:
		return response(user, res)

	result = run_command(user, _cmd_del(project, remote))
	return response(user, status=result['status'], body=result)
