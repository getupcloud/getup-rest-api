# -*- coding: utf-8 -*-

import bottle
import httpagentparser as _hap
import response

def is_browser(user_agent):
	if user_agent:
		ua = _hap.detect(user_agent)
		if ua:
			return ua.get('browser', {}).get('name', '')
	return ''

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
