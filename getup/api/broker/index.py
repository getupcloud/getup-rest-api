# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider, util
from getup.response import response

@aaa.authoritative_user
@provider.provider
def get(user, prov, path):
	url = prov(path)
	if bottle.request.body:
		res = url.GET(data=bottle.request.body, headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	else:
		res = url.GET(headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	return response(user, res)

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	return _data_request(user, prov(path).POST)

@aaa.authoritative_user
@provider.provider
def put(user, prov, path):
	return _data_request(user, prov(path).PUT)

@aaa.authoritative_user
@provider.provider
def delete(user, prov, path):
	return _data_request(user, prov(path).DELETE)

def _data_request(user, method):
	res = method(data=bottle.request.body, headers=dict(bottle.request.headers), cookies=bottle.request.cookies)
	return response(user, res)
