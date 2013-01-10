# -*- coding: utf-8 -*-

import bottle

def filter_headers(headers=['accept', 'host', 'authorization']):
	_headers = {}
	for k, v in bottle.request.headers.iteritems():
		if k.lower() not in headers:
			_headers[k] = v
	return _headers
