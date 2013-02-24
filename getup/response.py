# -*- coding: utf-8 -*-

import bottle
import http
import proto
import json
import StringIO

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
		headers['Status'] = code
		body = json.dumps(body)
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

#
# Our response object builder
#

class HTTPResponse(bottle.HTTPResponse):
	def __init__(self, body, status, user, res, *va, **kva):
		super(HTTPResponse, self).__init__(body=body, status=status, *va, **kva)
		# some handy stuff
		self.res = res
		self.req = res.request if res else None
		self.user = user
		self.ok = 400 > self.status_code >= 200
		try:
			self.json = json.loads(body.read())
		except AttributeError:
			self.json = json.loads(body)
		except:
			self.json = None

def response(user, res=None, status=http.HTTP_INTERNAL_SERVER_ERROR, body='', headers=None):
	assert res is not None or status is not None, 'response: error: invalid parameters'
	hdrs = { 'Cache-Control': 'no-cache' }
	if res is not None:
		exclude_headers = [ 'status' ]
		status_line = '%i %s' % (res.status_code, res.reason or res.raw.reason)
		hdrs.update([ (k, v) for (k,v) in res.headers.iteritems() if k.lower() not in exclude_headers ])
		body = res.json if isinstance(res.json, (dict, list, tuple)) else res.content
	else:
		status_line = '%i %s' % (status, http.responses(status))
	if headers:
		hdrs.update(headers)

	if isinstance(body, (dict, list, tuple)):
		body = json.dumps(body, indent=3)
		hdrs['Content-Type'] = 'application/json'

	return HTTPResponse(body=body, status=status_line, user=user, res=res, **hdrs)
