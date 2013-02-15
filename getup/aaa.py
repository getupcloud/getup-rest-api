# -*- coding: utf-8 -*-

import json
import bottle
import response, database

app = bottle.app()

#
# Authentication
#
def _get_auth_token(params, headers):
	return '', params.get('private_token', params.get('token'))

def _get_auth_basic(params, headers):
	try:
		username, password = bottle.request.auth
		return username, password
	except TypeError:
		return None, None

def _get_user():
	'''Read user/pass data from request using all known auth methods (token or basic).
		Load user data from DB and match passwords.
		Returns user object or None if failed.
	'''
	user = None
	for read_auth_data in [ _get_auth_token, _get_auth_basic ]:
		username, auth_token = read_auth_data(bottle.request.params, bottle.request.headers)
		if username:
			user = database.user(email=username)
			if user['authentication_token'] != auth_token:
				return False
		elif auth_token:
			user = database.user(authentication_token=auth_token)
		if user:
			return user
	return False

def _do_auth(predicate, response_class):
	app.config.user = _get_user()
	return app.config.user if app.config.user and predicate(app.config.user) else None

def _authenticate():
	'''Authenticate user from database with a given pass, set app.config.user to authenticated user,
		otherwise raises ResponseUnauthorized.
	'''
	user = _get_user()
	if not user or user.blocked:
		return response.ResponseUnauthorized()
	return user

def user(wrapped):
	'''User authentication decorator.
		Pass paramater 'user' into wrapped function.
	'''
	def wrapper(*vargs, **kvargs):
		user = _authenticate()
		return wrapped(user=user, *vargs, **kvargs)
	return wrapper

#
# Accounting
#
def _account(user, event, value):
	'''Register accounting event
	'''
	assert user,  'Accouting: invalid user'
	assert event, 'Accouting: missing event name'

	if not isinstance(value, basestring):
		value = json.dumps(value)
	database.accounting(user=user, event_name=event, event_value=value)

def create_app(user, app_data):
	fields = [ 'gear_count', 'embedded', 'name', 'domain_id' ]
	data = { field:app_data[field] for field in app_data if field in fields }
	return _account(user, event='create-app', value=data)

def delete_app(user, domain, application):
	return _account(user, event='delete-app', value={'name': application, 'domain_id': domain})

def scale_app(user, domain, application, events_data):
	event = events_data.get('event')
	if event in [ 'scale-up', 'scale-down' ]:
		return _account(user, event=event, value={'name': application, 'domain_id': domain})

def create_gear(user, domain, application, gear_data):
	cartridge = gear_data.get('name')
	return _account(user, event='create-gear', value={'name': cartridge, 'domain_id': domain, 'application': application})

def delete_gear(user, domain, application, cartridge):
	return _account(user, event='delete-gear', value={'name': cartridge, 'domain_id': domain, 'application': application})
