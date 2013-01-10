# -*- coding: utf-8 -*-

import base64
import bottle
import response, database

app = bottle.app()

def _auth_user():
	#todo: secure token
	try:
		if 'token' in bottle.request.params:
			kind, auth_token = 'token', bottle.request.params['token']
		elif 'Authorization' in bottle.request.headers:
			kind, auth_token = bottle.request.headers['Authorization'].split(None, 1)
		else:
			return False

		kind = kind.lower()
		if kind == 'basic':
			username, token = base64.decodestring(auth_token).split(':')
		elif kind == 'token':
			username, token = '', auth_token
		else:
			return False
	except ValueError:
		return False

	user = database.user(authentication_token=token, email=username)
	return user if user and user['authentication_token'] == token else False

def _do_auth(predicate, response_class):
	app.config.user = _auth_user()
	if predicate(app.config.user):
		return True
	return False

def admin_user(wrapped):
	def wrapper(*vargs, **kvargs):
		if not _do_auth(lambda u: u and u.admin and not u.blocked, response.ResponseForbidden):
			return response.ResponseForbidden()
		return wrapped(*vargs, **kvargs)
	return wrapper

def valid_user(wrapped):
	def wrapper(*vargs, **kvargs):
		if not _do_auth(lambda u: u and not u.blocked, response.ResponseUnauthorized):
			return response.ResponseUnauthorized()
		return wrapped(*vargs, **kvargs)
	return wrapper

def authoritative_user(wrapped):
	def wrapper(name=None, *vargs, **kvargs):
		if not name:
			name = app.config.user.email
		if name != app.config.user.email and name != app.config.user.id:
			if not app.config.user.admin:
				raise response.ResponseForbidden()
			try:
				user = database.user(id=int(name))
			except ValueError:
				user = database.user(email=name)
		else:
			user = app.config.user
		return wrapped(user=user, *vargs, **kvargs)
	return wrapper

@valid_user
@authoritative_user
def auth_user(user):
	return user
