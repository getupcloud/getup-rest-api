# -*- coding: utf-8 -*-

import unittest
from getup.response import *
from functools import wraps

_errors = {
	400: ResponseBadRequest,
	404: ResponseNotFound,
	#422: ResponseUnprocessableEntity,
	500: ResponseInternalServerError,
	409: ResponseConflict,
}

def response(res, description=None):
	try:
		status_code = res.status_code
		data = res.json['data']
	except AttributeError:
		return ResponseInternalServerError(description='Invalid response from provider (type=%s)' % res)

	ErrorClass = _errors.get(status, 500)
	return ErrorClass(data, description)


def make(klass, res, *vargs, **kvargs):
	'''Maps error codes to exception instance.
	'''
	http_error = res.status_code
	exit_code = res['messages'][0]['exit_code']
	text = res['messages'][0]['text']
	ErrorClass = klass._errors[http_error][exit_code]
	e = ErrorClass(response=ErrorClass.Response(description=text, **kvargs))
	print '[%s %s]' % (ErrorClass, e)
	return e

#
# Provider errors
#
class ProviderError(Exception):
	'''Generic provider error
	'''
	def __init__(self, response=None):
		assert isinstance(response, getup.response.APIResponse), 'invalid parameter: %s' % type(response)
		self.response = response

#
# Domain errors
#
class DomainError(ProviderError):
	'''Generic domain errors
	'''
	_errors = {}

	@staticmethod
	def make_error(res, *vargs, **kvargs):
		return make(DomainError, res, *vargs, **kvargs)

class DomainNotFoundError(DomainError):
	'''Domain not found
	'''

#@register_error(DomainError, 404, 101)
class DomainExistsError(DomainError):
	'''Domain already exists
	'''


#
# App errors
#
class AppError(ProviderError):
	'''Generic app error
	'''
	_errors = {}

	@staticmethod
	def make_error(res, *vargs, **kvargs):
		return make(AppError, res, *vargs, **kvargs)

#@register_error(AppError, 404, 101)
class AppNotFoundError(AppError):
	'''App not found
	'''
	Response = ResponseNotFound

#@register_error(AppError, 422, 109, 134, 125)
class AppCreateError(AppError):
	'''Unable to create app
	'''
	Response = ResponseBadRequest

#@register_error(AppError, 422, 100)
class AppExistsError(AppError):
	'''App already exists
	'''
	Response = ResponseConflict

class AppScaleError(AppError):
	'''Unable to scale up or down
	'''

class AppConfigureError(AppError):
	'''Unable to set app configuration
	'''

class TestErrors(unittest.TestCase):
	class FakeResult:
		def __init__(self, status_code, exit_code, text):
			self.status_code = status_code
			self.data = {'messages': [ { 'exit_code': exit_code, 'text': text } ] }
		def __getitem__(self, name):
			return self.data[name]

	errors = {
	#	(FakeResult(422, 100, 'fake 422 100'), AppError),
	}

	def test_app_errors(self):
		for res, ex in self.errors:
			print res, '--', ex,'--', AppError.make_error(res)
			self.assertTrue(isinstance(AppError.make_error(res), type(ex)))

if __name__ == '__main__':
	print 'testing...'
	unittest.main()
