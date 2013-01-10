# -*- coding: utf-8 -*-

import bottle
import requests
from getup import http, proto

class Exposable:
	_expose = []
	def __init__(self):
		pass

	def expose(self):
		for f in self._expose:
			yield (f, getattr(self, f))

class APIResponse(bottle.HTTPResponse):
	'''Default http response (500)
	'''
	def __init__(self, status=http.HTTP_INTERNAL_SERVER_ERROR, description=None, headers={}, **data):
		#if isinstance(data, requests.Response):
		#	data = {
		#				'method': data.request.method, 'content': data.request.data or '',
		#				'url': data.url, 'status_code': data.status_code
		#	}
		#try:
		#	data = dict(data.expose())
		#except AttributeError:
		#	pass
		_data = {}
		for k, v in data.iteritems():
			try:
				_data[k] = v.expose()
			except AttributeError:
				_data[k] = v

		#self.status = status
		#code, message = self.status.split(None, 1)
		code, message = status, bottle.HTTP_CODES[status]
		body = {
			'status': { 'code': code, 'message': message },
			'data': data,
		}
		if isinstance(description, basestring):
			body['status']['description'] = description
		from getup import codec
		body = codec.json_codec.encode(body)
		bottle.HTTPResponse.__init__(self, body=body, status=status, header={'Content-Type': 'application/json'}, **headers)

class ResponseInternalServerError(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_INTERNAL_SERVER_ERROR, **data)

class ResponseOK(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_OK, **data)

class ResponseMultipleChoices(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_MULTIPLE_CHOICES, **data)

class ResponseNotFound(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_NOT_FOUND, **data)

class ResponseCreated(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_CREATED, **data)

class ResponseConflict(APIResponse):
	def __init__(self, description=None, **data):
		APIResponse.__init__(self, status=http.HTTP_CONFLICT, description=description, **data)

class ResponseMethodNotAllowed(APIResponse):
	def __init__(self):
		APIResponse.__init__(self, status=http.HTTP_METHOD_NOT_ALLOWED, description='Sorry, method not alllowed')

class ResponseBadRequest(APIResponse):
	def __init__(self, description='Sorry, request parameters not understood', **data):
		APIResponse.__init__(self, status=http.HTTP_BAD_REQUEST, description=description, **data)

def _format_parameters(invalid, mandatory=None, optional=None):
		return {
			'invalid': invalid,
			'mandatory': mandatory or [],
			'optional': optional or {}
		}

class ResponseMissingParameter(ResponseBadRequest):
	def __init__(self, names, mandatory=None, optional=None):
		ResponseBadRequest.__init__(self, description='Missing parameter',
			**_format_parameters(names, mandatory, optional))

class ResponseInvalidParameter(ResponseBadRequest):
	def __init__(self, names, mandatory=None, optional=None):
		ResponseBadRequest.__init__(self, description='Invalid parameter',
			**_format_parameters(names, mandatory, optional))

class ResponseInvalidParameterType(ResponseBadRequest):
	def __init__(self, names, mandatory=None, optional=None):
		ResponseBadRequest.__init__(self, description='Invalid parameter type',
			**_format_parameters(names, mandatory, optional))

class ResponseDuplicatedParameter(ResponseBadRequest):
	def __init__(self, names, mandatory=None, optional=None):
		ResponseBadRequest.__init__(self, description='Duplicated parameter',
			**_format_parameters(names, mandatory, optional))

def _auth_method():
	if proto.is_browser(bottle.request.get_header('user_agent', '')):
		return 'Basic realm="GetUP Cloud Rest API"'
	else:
		return 'Token'

class ResponseUnauthorized(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_UNAUTHORIZED, headers={'WWW-Authenticate': _auth_method()}, **data)

class ResponseForbidden(APIResponse):
	def __init__(self, **data):
		APIResponse.__init__(self, status=http.HTTP_FORBIDDEN, headers={'WWW-Authenticate': _auth_method()}, **data)

exclude_headers = [ 'status' ]

def response(user, res):
	status_line = '%i %s' % (res.status_code, res.reason or res.raw.reason)
	headers = dict([ (k, v) for (k,v) in res.headers.iteritems() if k.lower() not in exclude_headers ])
	resp = bottle.HTTPResponse(body=res.content, status=status_line, header={'Cache-Control': 'no-cache'})
	if not hasattr(resp, 'request'):
		setattr(resp, 'request', res.request)
	if not hasattr(resp, 'user'):
		setattr(resp, 'user', user)
	return resp
