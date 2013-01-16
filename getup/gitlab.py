import bottle
from hammock import Hammock
from functools import wraps

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
		hdr = { app.config.webgit['token_header']: app.config.user['authentication_token'] }
		self.api = Hammock(app.config.webgit['base_url'].rstrip('/'), headers=hdr)

	def __getattr__(self, name):
		return getattr(self.api, name)

	def add_key(self, body, **kvargs):
		return self.api.api.v2.user.keys.POST(data=body, **kvargs)

def api(wrapped):
	@wraps(wrapped)
	def wrapper(user, *vargs, **kvargs):
		return wrapped(user=user, api=Gitlab(), *vargs, **kvargs)
	return wrapper
