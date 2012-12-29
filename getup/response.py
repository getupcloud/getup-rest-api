# -*- coding: utf-8 -*-

import bottle
from getup import version, http, codec

class APIBaseResponse(bottle.HTTPResponse):
	'''Default http response (500)
	'''
	def __init__(self, status=http.HTTP_INTERNAL_SERVER_ERROR, data=None, **headers):
		if data is None:
			data = []
		elif not isinstance(data, (list, tuple)):
			data = [ data ]
		bottle.HTTPResponse.__init__(self, header={'Content-Type': 'application/json'}, **headers)
		self.status = status
		code, message = self.status.split(None, 1)
		body = {
			'status': { 'code': code, 'message': message },
			'data': data,
		}
		self._body = body
		self.body = codec.json.encode(self._body)

class ResponseOK(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_OK, data=data, **headers)

class ResponseMultipleChoices(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_MULTIPLE_CHOICES, data=data, **headers)

class ResponseNotFound(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_NOT_FOUND, data=data, **headers)

class ResponseCreated(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_CREATED, data=data, **headers)

class ResponseBadRequest(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_BAD_REQUEST, data=data, **headers)

def _auth_method():
	if is_browser(bottle.request.get_header('user_agent', '')):
		return 'Basic realm="GetUP Cloud Rest API"'
	else:
		return 'Token'

class ResponseUnauthorized(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_UNAUTHORIZED, data=data, www_authenticate=_auth_method(), **headers)

class ResponseForbidden(APIBaseResponse):
	def __init__(self, data=None, **headers):
		APIBaseResponse.__init__(self, status=http.HTTP_FORBIDDEN, data=data, www_authenticate=_auth_method(), **headers)
