# -*- coding: utf-8 -*-

import bottle
import response, database
import base64
import json

app = bottle.app()

def _get_auth_token(params, headers):
	return '', params.get('private_token', params.get('token'))

def _get_auth_basic(params, headers):
	try:
		token = headers['Authorization']
		auth_type, auth_token = token.split(None, 1)
		if auth_type.lower() == 'basic':
			return tuple(base64.decodestring(auth_token).split(':', 1)[:2])
	except:
		pass
	return None, None

def _auth_user():
	#todo: secure token
	for authenticator in [ _get_auth_token, _get_auth_basic ]:
		username, auth_token = authenticator(bottle.request.params, bottle.request.headers)
		if auth_token:
			user = database.user(authentication_token=auth_token, email=username)
			if user and user['authentication_token'] == auth_token:
				return user
	return False

def _do_auth(predicate, response_class):
	app.config.user = _auth_user()
	return True if predicate(app.config.user) else False

def admin_user(wrapped):
	'''Decorator to enforce an admin user only.
	'''
	def wrapper(*vargs, **kvargs):
		if not _do_auth(lambda u: u and u.admin and not u.blocked, response.ResponseForbidden):
			return response.ResponseForbidden()
		return wrapped(*vargs, **kvargs)
	return wrapper

def valid_user(wrapped):
	'''Decorator to enforce a valid authenticated user.
	'''
	def wrapper(*vargs, **kvargs):
		if not _do_auth(lambda u: u and not u.blocked, response.ResponseUnauthorized):
			return response.ResponseUnauthorized()
		return wrapped(*vargs, **kvargs)
	return wrapper

def authoritative_user(wrapped):
	'''Decorator to query and validate an authenticated user.
	It receives the username as parameter "username" and passes the user
	record from database as parameters "user" to wrapped function.
	Admin users can query any user.
	'''
	def wrapper(username=None, *vargs, **kvargs):
		if username is None:
			username = app.config.user.email
		if username != app.config.user.email and username != app.config.user.id:
			if not app.config.user.admin:
				raise response.ResponseForbidden()
			try:
				user = database.user(id=int(username))
			except ValueError:
				user = database.user(email=username)
			if not user:
				raise response.ResponseForbidden()
		else:
			user = app.config.user
		return wrapped(user=user, *vargs, **kvargs)
	return wrapper

@valid_user
@authoritative_user
def auth_user(user):
	return user

def accounting(**labels):
	'''Decorator to account HTTP requests. Only HTTP status 2xx are accounted.
	To specify what HTTP method to account for, pass it as parameter in the
	format "method-name=(event-name, result-filter=None, data-filter=None)"

	A "result-filter" callback can be specified to validate if the request should
	or not be accounted. This callback must be a callable and must evaluate to
	True to activate accounting, otherwise accouting is not done for the current
	request only. It receives a single parameter, the returned value from the
	wrapped function.

	In order to filter the accounted data, one can supply a "data-filter". It receives
	the request's body and returns the saved event-value. The returned value is
	jsonifyed prior to save.

	Both "result-filter" and "data-filter" can be ommited. In this case, the format
	is simplified to "method-name=event-name".

	Example:

		# some result-callback
		def validate_delete(res):
			# account only for HTTP 204
			return res.status_code == 204

		@bottle.route('/')
		@accounting(POST='create_app', DELETE=('delete_app', validate_delete))
		def root_handler():
			return 'OK'
	'''
	class Accounter:
		def __init__(self, wrapped):
			if not labels:
				raise ValueError('Missing accounting labels')
			self.wrapped = wrapped
			self.labels = labels
			for l in labels.values():
				if not isinstance(l, (basestring, list, tuple, dict)):
					raise TypeError('Invalid accounting label: %r' % l)
		def __call__(self, *vargs, **kvargs):
			res = self.wrapped(*vargs, **kvargs)

			# check if this method must be accounted
			label = self.labels.get(bottle.request.method, None)
			if label is None:
				return res

			# check if result and data callbacks was supplied
			filter_callback, filter_data_callback = None, None
			try:
				event_name           = label['event-name']
				filter_callback      = label.get('result-callback', None)
				filter_data_callback = label.get('data-callback', None)
			except (TypeError, AttributeError):
				if len(label) == 3:
					event_name, filter_callback, filter_data_callback = label
				elif len(label) == 2:
					event_name, filter_callback = label
				else:
					event_name = label

			if callable(filter_callback):
				if not filter_callback(res):
					return res

			if callable(filter_data_callback):
				save_data = filter_data_callback(bottle.request.body)
			else:
				save_data = bottle.request.body

			if 200 <= res.status_code < 300:
				event_value = {
					'req_url': res.request.path_url,
					'req_data': save_data,
					'res_status': res.status_code,
				}
				account(user=res.user, event_name=event_name, event_value=event_value)
			return res
	return Accounter

def account(user, event, value):
	'''Register accounting event
	'''
	if not isinstance(value, basestring):
		value=json.dumps(value)
	database.accounting(user=user, event_name=event, event_value=value)

def create_app(user, app_data):
	return account(user, event='create-app', value=app_data)

def delete_app(user, app_data):
	return account(user, event='delete-app', value=app_data)

def create_gear(user, gear_name):
	return account(user, event='create-gear', value={'name':gear_name})

def delete_gear(user, gear_name):
	return account(user, event='delete-gear', value={'name':gear_name})
