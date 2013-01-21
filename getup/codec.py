# -*- coding: utf-8 -*-

import bottle
from json import loads as json_loads, dumps as json_dumps
import ast
import response

class Codec:
	def __init__(self):
		pass
	def encode(self, data):
		pass
	def decode(self, data):
		pass

class NullCodec(Codec):
	def encode(self, data=None): return data
	def decode(self, data=None): return data if data is not None else bottle.request.body.read(-1)

class JsonCodec(Codec):
	def encode(self, data, *vargs, **kvargs):
		def _encoder(o):
			#TODO: extend
			return str(o)
		return json_dumps(data, indent=2, default=_encoder)

	def decode(self, data=None):
		return bottle.request.json if data is None else json_loads(data)

class FormURLCodec(Codec):
	def encoode(self, **data):
		raise NotImplemented

	def decode(self, data=None):
		return bottle.request.params

null_codec = NullCodec()
json_codec = JsonCodec()
form_urlencoded_codec = FormURLCodec()

null = {
	'content_type': [ '*/*' ],
	'codec': null_codec,
}

json = {
	'content_type': [ 'application/json' ],
	'codec': json_codec,
}

form_urlencoded = {
	'content_type': [ 'application/x-www-form-urlencoded',  ],
	'codec': form_urlencoded_codec,
}

def decode(codec, varname='request_data'):
	class DecodeContent:
		def __init__(self, wrapped):
			try:
				self._codec = codec['codec']
			except TypeErro:
				self._codec = codec
			self._wrapped = wrapped
			self._varname = varname
		def __call__(self, *vargs, **kvargs):
			data = self._codec.decode()
			kvargs.update((self._varname, data))
			return self._wrapped(*vargs, **kvargs)
	return DecodeContent

def decoder(varname='request_data', *codecs):
	'''Decorator to decode content from request.
	Parameter "codecs" is a list of codec-objects (ex: json, urlencoded).
	The decoded content is passed to decorated() via parameter named after 'varname'.
	'''
	class DecodeContent:
		def __init__(self, wrapped):
			self._codecs = codecs
			self._wrapped = wrapped
			self._varname = varname
		def __call__(self, *vargs, **kvargs):
			codec = None
			content_type = bottle.request.content_type
			if content_type:
				for c in self._codecs:
					if content_type in c['content_type']:
						codec = c['codec']
						break
				if not codec:
					raise response.ResponseBadRequest('Unsupported Content Type')
			data = (codec or null_codec).decode()
			kvargs.update((self._varname, data))
			return self._wrapped(*vargs,**kvargs)
	return DecodeContent

def parse_params(*mandatory, **optional):
	'''Decorator to parse parameter from request. The content to parse from
	must be a dict-like object. There are two types of parameters: "mandatory" and "optional".
	The later is defined by having a default value.
	The decorated method will expect a parameter named "request_data" to receive the
	request content as a dict-like object.
	'''
	class ParseParameters:
		def __init__(self, wrapped):
			self._params_mandatory = mandatory
			self._params_optional  = optional
			self._wrapped = wrapped
		def __call__(self, request_data=None, *vargs, **kvargs):
			# retrieve raw content to parse
			if request_data is None:
				# default is json from bottle
				if bottle.request.json:
					request_data = bottle.request.json
				else:
					raise response.ResponseInternalServerError(description='Invalid content (missing codec?)')
			params = {}
			parsed_val_ns = {}
			if not hasattr(request_data, 'iteritems'):
				raise response.ResponseBadRequest('Invalid Content')
			for k, v in request_data.iteritems():
				# check mandatory items
				if k not in self._params_mandatory and k not in self._params_optional:
					raise response.ResponseInvalidParameter(k, self._params_mandatory, self._params_optional)
				elif k in params:
					raise response.ResponseDuplicatedParameter(k, self._params_mandatory, self._params_optional)

				try:
					_p = self._params_optional[k]
					_v = ast.literal_eval(v)
					# enforce same types
					if _v is not None and type(_v) != type(_p):
						raise response.ResponseInvalidParameterType(k, self._params_mandatory, self._params_optional)
				except KeyError:
					_v = v
				except SyntaxError:
					raise response.ResponseInvalidParameter(k, self._params_mandatory, self._params_optional)

				params[k] = _v

			# check if all mandatory items was supplied
			for p in self._params_mandatory:
				if p not in params:
					raise response.ResponseMissingParameter(p, self._params_mandatory, self._params_optional)

			# fill in any missing optional parameter
			for k, v in self._params_optional.iteritems():
				if k not in params:
					params[k] = v
			params.update(kvargs)

			return self._wrapped(*vargs, **params)
	return ParseParameters
