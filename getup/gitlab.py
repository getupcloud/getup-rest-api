import bottle
from hammock import Hammock
from functools import wraps
from openssh_wrapper import SSHConnection
import json, os

app = bottle.app()

def user(userid=None, token=None):
	hdr = { app.config.webgit['token_header']: token or app.config.user.authentication_token }
	users = Hammock('https://' + app.config.webgit['hostname'], headers=hdr).users
	if userid:
		u = users.GET(userid).json
		u['keys'] = user.keys.GET(verify=False).json
		return [ u ]
	else:
		users = Hammock('https://' + app.config.webgit['hostname'], headers=hdr).users
	return users.GET(verify=False).json

def session(body):
	gitlab = Hammock('https://' + app.config.webgit['hostname'])
	hdrs = {'Content-Type': 'application/json'}
	return gitlab.api.v2.session.POST(verify=False, data=body, headers=hdrs)

class Gitlab:
	def __init__(self):
		self.headers = {
			app.config.webgit['token_header']: app.config.user['authentication_token'],
			'Content-Type': 'application/json',
		}
		self.api = Hammock('https://' + app.config.webgit['hostname'].rstrip('/'), headers=self.headers)

	def __getattr__(self, name):
		return getattr(self.api, name)

	def add_project(self, name, **kvargs):
		return self.api.api.v2.projects.POST(verify=False, name=json.dumps({'name': name}), **kvargs)

	def get_project(self, name=None, **kvargs):
		if name:
			return self.api.api.v2.projects(name).GET(verify=False, **kvargs)
		else:
			return self.api.api.v2.projects.GET(verify=False)

	def add_key(self, title, key, headers=None, **kvargs):
		hdrs = self.headers
		if headers:
			hdrs.update(headers)
		hdrs['Content-Type'] = 'application/json'
		body = {'title': title, 'key': key }
		return self.api.api.v2.user.keys.POST(verify=False, data=json.dumps(body), headers=hdrs, **kvargs)

	def del_key(self, id, headers=None, **kvargs):
		hdrs = self.headers
		if headers:
			hdrs.update(headers)
		return self.api.api.v2.user.keys(id).DELETE(verify=False, headers=hdrs, **kvargs)

#def api(wrapped):
#	@wraps(wrapped)
#	def wrapper(user, *vargs, **kvargs):
#		return wrapped(user=user, api=Gitlab(), *vargs, **kvargs)
#	return wrapper

def SSHClient():
	conf = app.config.webgit
	params = {
		'server': conf['hostname'],
		'login':  conf['git_user'],
	}
	if 'port' in conf:
		params['port'] = conf['port']
	if 'identity_file' in conf:
		params['identity_file'] = conf['identity_file']

	return SSHConnection(**params)

'''
def ssh(wrapped):
	@wraps(wrapped)
	def wrapper(*va, **kva):
		conf = app.config.webgit
		params = {
			'server': conf['hostname'],
			'login':  conf['git_user'],
		}
		if 'port' in conf:
			params['port'] = conf['port']
		if 'identity_file' in conf:
			params['identity_file'] = os.path.expanduser(conf['identity_file'])

		conn = SSHConnection(**params)
		kva['ssh'] = conn
		ret = wrapped(*va, **kva)
		return ret
	return wrapper
'''
