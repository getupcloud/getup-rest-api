# -*- coding: utf-8 -*-

from http import *
from api import version as api_version
from api import User, Domain, App

class Response(dict):
	def __init__(self, data=None, code=HTTP_OK, message='OK'):
		self.status_code = code
		self.status_message = message
		self['status'] = dict(code=code, message=message, api_version=api_version)
		self['data'] = data

class ResponseCreated(Response):
	def __init__(self, data=None):
		Response.__init__(self, data, code=HTTP_CREATED, message='Created')

class ResponseBadRequest(Response):
	def __init__(self, data=None):
		Response.__init__(self, data, code=HTTP_BAD_REQUEST, message='Bad Request')

'''
class Discovery(Response):
	def __init__(self, **kvargs):
		Response.__init__(self, data=kvargs)
'''
