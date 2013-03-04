# -*- coding: utf-8 -*-

import json
import bottle
import provider
import http
import gitlab
from response import response, HTTPResponse
from datetime import datetime
import collections
import socket
import dns.query
import dns.tsigkeyring
import dns.update
import dns.tsig

Application = collections.namedtuple('Application', 'domain name cartridge scale gear_profile')
Project = collections.namedtuple('Project', 'name application dev_application')

app = bottle.app()

def _cmd_list(project, cmd='list'):
	return '{bin} {cmd} {project}'.format(
		bin=app.config.webgit.remotes_bin, cmd=cmd, project=project)

def _cmd_create(project, name, url, cmd):
	return '{bin} {cmd} {project} {name} "{url}"'.format(
		bin=app.config.webgit.remotes_bin, cmd=cmd, project=project, name=name, url=url)

def _cmd_del(project, name, cmd='del'):
	return '{bin} {cmd} {project} {name}'.format(
		bin=app.config.webgit.remotes_bin, cmd=cmd, project=project, name=name)

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
		print 'Failure parsing command output: {ex}'.format(ex=ex)
		print '--- stdout'
		print cmd_result.stdout
		print '--- stderr'
		print cmd_result.stderr
		print '---'
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

	remote = '{app[name]}-{app[domain_id]}'.format(app=app_data)
	git_url = '{app[ssh_url]}/~/git/{app[name]}.git/'.format(app=app_data)
	return run_command(user, _cmd_create(project, remote, git_url, command))

def _install_getup_key(user):
	try:
		with open(app.config.webgit.pubkey_file) as fp:
			prov = provider.OpenShift(user)
			i = 0
			for line in fp:
				keyparts = tuple(line.strip().split())
				if not keyparts or keyparts[0].startswith('#'):
					continue
				((key_type, content), name) = (keyparts[:2], 'getupcloud%i' % i)
				res = prov.add_key(name=name, content=content, type=key_type)
				if res.status_code not in [ http.HTTP_CREATED, http.HTTP_CONFLICT ]:
					print 'WARNING: error posting getup pub-key {name} ({key_type}) to user {user}: {res.status_code} {res.raw.reason}'.format(
						name=name, key_type=key_type, user=user['email'], res=res)
				i += 1
				print 'installed getup pub-key {name} ({key_type}) {key_prefix}...{key_suffix}'.format(
					name=name, key_type=key_type, key_prefix=content[:8], key_suffix=content[-8:])
	except Exception, ex:
		print 'WARNING: unable to install getup pub-key to user {user}: {ex.__class__}: {ex}'.format(
			user=user['email'], ex=ex)

#
# Commands
#
def clone_remote(user, project_name, application):
	_install_getup_key(user)
	mesg = 'setup application project repository: app={app.name}-{app.domain} project={project}'.format(app=application, project=project_name)
	print mesg
	res = _create_remote(user, project_name, application.domain, application.name, 'clone')
	print '{mesg} (end with {status})'.format(mesg=mesg, status=res.get('status'))
	return response(user, status=res['status'], body=res)

def add_remote(user, project_name, application):
	_install_getup_key(user)
	mesg = 'attaching repository into application: app={app.name}-{app.domain} project={project}'.format(app=application, project=project_name)
	print mesg
	res = _create_remote(user, project_name, application.domain, application.name, 'add')
	print '{mesg} (end with {status})'.format(mesg=mesg, status=res.get('status'))
	return response(user, status=res.get('status'), body=res)

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
		return res

	res = provider.OpenShift(user).add_dom(app.domain)
	if res.ok:
		print 'Domain created:', app.domain
		return res

	raise response(user, res=res)

def _create_gitlab_project(user, proj):
	res = gitlab.Gitlab().add_project(name=proj.name)
	if res.ok:
		print 'Project created:', proj.name
		return res

	raise response(user, res=res)

def _create_application(user, app):
	res = provider.OpenShift(user).add_app(**app._asdict())
	if res.ok:
		print 'Application created: {app.name}-{app.domain}'.format(app=app)
		return res

	raise response(user, res=res)

def _clone_app_into_repo(user, project_name, application):
	res = clone_remote(user, project_name, application)
	if res.ok:
		print 'Project cloned from application: {app.name}-{app.domain} -> {project}'.format(
			app=application, project=project_name)
		return res

	raise res

def _add_remote(user, project_name, application):
	res = add_remote(user, project_name, application)
	if res.ok:
		print 'Remote added to project: {project} -> {app.name}-{app.domain}'.format(
			app=application, project=project_name)
		return res

	raise res

def create_project(user, project):
	start_time = datetime.utcnow().ctime()

	report = []
	def add_report(action, description, **kva):
		report.append(dict(action=action, description=description, **kva))

	def set_report_status(res):
		r = report[-1]
		print '{action}: {res.status_code}\n---\n{res.json}\n---'.format(
			action=r['action'], res=res)
		report[-1].update(status=res.status_code, content=res.json)

	try:
		# create openshift domain
		add_report('domain', 'Create openshift domain')
		res = _create_domain(user, project.application)
		set_report_status(res)

		# create gitlab project
		add_report('project', 'Create project repository')
		res = _create_gitlab_project(user, project)
		set_report_status(res)

		# create openshift app
		add_report('application', 'Create openshift application')
		res = _create_application(user, project.application)
		set_report_status(res)

		# clone and setup default remote
		add_report('clone', 'Clone and setup application code into project repository')
		res = _clone_app_into_repo(user, project.name, project.application)
		set_report_status(res)

		# create dev openshift app is applicable
		if project.dev_application:
			add_report('dev_application', 'Create openshift dev_application')
			res = _create_application(user, project.dev_application)
			set_report_status(res)

			dns_register_wildcard_cname('{app.name}-{app.domain}'.format(app=project.dev_application))
			#set_report_status(res)

			# add remote to dev repoitory
			add_report('dev_remote', 'Add dev_application as remote')
			res = add_remote(user, project.name, project.dev_application)
			set_report_status(res)

	except HTTPResponse, ex:
		set_report_status(ex.res)
		add_report('finish', 'Failure creating component ({action})'.format(action=report[-1]['action']), status=str(),
			start_time=start_time, end_time=datetime.utcnow().ctime())
		return response(user, status=ex.status_code, body=report)

	add_report('finish', 'All operations sucessfully finished', start_time=start_time, end_time=datetime.utcnow().ctime())
	return response(user, status=http.HTTP_CREATED, body=report)

def dns_register_wildcard_cname(name):
	'''Creates a DNS CNAME entry '*.{name}' to '{name}'
	'''

	assert name, 'Invalid parameters to DNS UPDATE: name={name}'.format(name=name)
	zone = app.config.dns.zone
	key  = app.config.dns.key

	server = socket.getaddrinfo(app.config.dns.server, app.config.dns.port, socket.SOCK_DGRAM, 0, socket.SOL_UDP)
	if not server:
		raise response(user=None, status=http.HTTP_INTERNAL_SERVER_ERROR, body="Unable to resolve DNS server: {server}:{port}".format(**app.config.dns))
	server = server[0]
	af = server[0]
	addr, port = server[-1][:2]

	cname = '*.{name}'.format(name=name)
	print 'Registering DNS CNAME: {cname} -> {name}.{zone}'.format(cname=cname, name=name, zone=zone)
	keyring = dns.tsigkeyring.from_text({ zone: key })
	update = dns.update.Update(zone, keyring=keyring, keyname=zone, keyalgorithm=dns.tsig.HMAC_MD5)
	update.add(cname, 60, 'cname', name)
	response = dns.query.udp(update, where=addr, port=port, timeout=30, af=af)
	print 'DNS response\n---\n', response.to_text(), '\n---'
