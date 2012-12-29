import bottle
from hammock import Hammock

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

class Gitlab(Hammock):
	def __init__(self, authentication_token):
		hdr = { app.config.webgit['token_header']: authentication_token or app.config.user['authentication_token'] }
		Hammock.__init__(self, app.config.webgit['base_url'], headers=hdr)
