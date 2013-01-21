import bottle
from hammock import Hammock
from functools import wraps
import paramiko
import json, os

app = bottle.app()

def user(userid=None, token=None):
	hdr = { app.config.webgit['token_header']: token or app.config.user.authentication_token }
	users = Hammock('http://' + app.config.webgit['hostname'], headers=hdr).users
	if userid:
		u = users.GET(userid).json
		u['keys'] = user.keys.GET().json
		return [ u ]
	else:
		users = Hammock('http://' + app.config.webgit['hostname'], headers=hdr).users
	return users.GET().json

class Gitlab:
	def __init__(self):
		self.headers = {
			app.config.webgit['token_header']: app.config.user['authentication_token'],
			'Content-Type': 'application/json',
		}
		self.api = Hammock('http://' + app.config.webgit['hostname'].rstrip('/'), headers=self.headers)

	def __getattr__(self, name):
		return getattr(self.api, name)

	def add_key(self, title, key, headers=None, **kvargs):
		hdrs = self.headers
		if headers:
			hdrs.update(headers)
		hdrs['Content-Type'] = 'application/json'
		body = {'title': title, 'key': key }
		return self.api.api.v2.user.keys.POST(data=json.dumps(body), headers=hdrs, **kvargs)

	def del_key(self, id, headers=None, **kvargs):
		hdrs = self.headers
		if headers:
			hdrs.update(headers)
		return self.api.api.v2.user.keys(id).DELETE(headers=hdrs, **kvargs)

def api(wrapped):
	@wraps(wrapped)
	def wrapper(user, *vargs, **kvargs):
		return wrapped(user=user, api=Gitlab(), *vargs, **kvargs)
	return wrapper

def ssh(wrapped, varname='ssh'):
	class SSHClient:
		def __init__(self, *va, **kva):
			self.wrapped = wrapped
			self.varname = varname
			self.sshcli = paramiko.SSHClient()
			self.sshcli.load_system_host_keys()
			conf = app.config.webgit
			self.params = {
				hostname: conf['hostname'],
				username: conf['git_user'],
			}
			if 'identity_file' in conf:
				self.params['key_filename'] = os.path.expanduser(conf['identity_file'])
			self.sshcli.connect(compress=True, **params)
			self.va = va
			self.kva = kva
		def __call__(self, *va, **kva):
			kva[self.varname] = self.sshcli
			return self.wrapped(*self.va, *va, *self.kva, **kva)
	return SSHClient
