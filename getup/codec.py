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

def decode(codec):
	class DecodeContent:
		def __init__(self, wrapped):
			try:
				self._codec = codec['codec']
			except TypeErro:
				self._codec = codec
			self._wrapped = wrapped
		def __call__(self, *vargs, **kvargs):
			data = self._codec.decode()
			return self._wrapped(*vargs, content=data if data is not None else '', **kvargs)
	return DecodeContent

def decoder(*codecs):
	class DecodeContent:
		def __init__(self, wrapped):
			self._codecs = codecs
			self._wrapped = wrapped
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
			return self._wrapped(*vargs, content=data if data is not None else '', **kvargs)
	return DecodeContent

def parse_params(*mandatory, **optional):
	class ParseParameters:
		def __init__(self, wrapped):
			self._params_mandatory = mandatory
			self._params_optional  = optional
			self._wrapped = wrapped
		def __call__(self, content=None, *vargs, **kvargs):
			if content is None:
				raise response.ResponseInternalServerError(description='Invalid content (missing codec?)')
			params = {}
			parsed_val_ns = {}
			if not hasattr(content, 'iteritems'):
				raise response.ResponseBadRequest('Invalid Content')
			for k, v in content.iteritems():
				if k not in self._params_mandatory and k not in self._params_optional:
					raise response.ResponseInvalidParameter(k, self._params_mandatory, self._params_optional)
				elif k in params:
					raise response.ResponseDuplicatedParameter(k, self._params_mandatory, self._params_optional)

				try:
					_p = self._params_optional[k]
					_v = ast.literal_eval(v)
					if _v is not None and type(_v) != type(_p):
						raise response.ResponseInvalidParameterType(k, self._params_mandatory, self._params_optional)
				except KeyError:
					_v = v
				except SyntaxError:
						raise response.ResponseInvalidParameter(k, self._params_mandatory, self._params_optional)

				params[k] = _v

			for p in self._params_mandatory:
				if p not in params:
					raise response.ResponseMissingParameter(p, self._params_mandatory, self._params_optional)

			for k, v in self._params_optional.iteritems():
				if k not in params:
					params[k] = v
			params.update(kvargs)
			return self._wrapped(*vargs, **params)
	return ParseParameters
