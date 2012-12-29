# -*- coding: utf-8 -*-

import bottle
from json import loads as json_loads, dumps as json_dumps

class Codec:
	def __init__(self):
		pass
	def encode(self, data):
		pass
	def decode(self, data):
		pass

class JsonCodec(Codec):
	def encode(self, data=None):
		def _encoder(o):
			#TODO: extend
			return str(o)
		return json_dumps(data, indent=2, default=_encoder)

	def decode(self, data=None):
		return bottle.request.json if data is None else json_loads(data)

json = JsonCodec()

def decode(codec):
	class DecodeContent:
		def __init__(self, wrapped):
			self._codec = codec
			self._wrapped = wrapped
		def __call__(self, *vargs, **kvargs):
			data = self._codec.decode()
			return self._wrapped(*vargs, content=data, **kvargs)
	return DecodeContent

def content_type(typename):
	class CheckContentType:
		def __init__(self, wrapped):
			self._types = [ typename ] if isinstance(typename, basestring) else typename
			self._wrapped = wrapped
		def __call__(self, *vargs, **kvargs):
			if bottle.request.content_type not in self._types:
				raise response.ResponseBadRequest('unsupported content type')
			return self._wrapped(*vargs, **kvargs)
	return CheckContentType
