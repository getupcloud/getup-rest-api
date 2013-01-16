import bottle
from hammock import Hammock
from functools import wraps
import json

app = bottle.app()

def user(userid=None, token=None):
	hdr = { app.config.webgit['token_header']: token or app.config.user.authentication_token }
	users = Hammock(app.config.webgit['base_url'], headers=hdr).users
	if userid:
		u = users.GET(userid).json
		u['keys'] = user.keys.GET().json
		return [ u ]
	else:
		users = Hammock(app.config.webgit['base_url'], headers=hdr).users
	return users.GET().json

class Gitlab:
	def __init__(self):
		self.headers = {
			app.config.webgit['token_header']: app.config.user['authentication_token'],
			'Content-Type': 'application/json',
		}
		self.api = Hammock(app.config.webgit['base_url'].rstrip('/'), headers=self.headers)

	def __getattr__(self, name):
		return getattr(self.api, name)

	def add_key(self, body, headers=None, **kvargs):
		hdrs = self.headers
		if headers:
			hdrs.update(headers)
		hdrs['Content-Type'] = 'application/json'
		return self.api.api.v2.user.keys.POST(data=json.dumps(body), headers=hdrs, **kvargs)

def api(wrapped):
	@wraps(wrapped)
	def wrapper(user, *vargs, **kvargs):
		return wrapped(user=user, api=Gitlab(), *vargs, **kvargs)
	return wrapper
