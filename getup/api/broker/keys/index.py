# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider
from getup.response import response

@aaa.authoritative_user
@provider.provider
def post(user, prov, api, path):
	return 'OK\n'
	return _data_request(user, prov(path).POST)

@aaa.authoritative_user
@provider.provider
def put(user, prov):
	return _data_request(user, prov(path).PUT)

@aaa.authoritative_user
@provider.provider
def delete(user, prov):
	return _data_request(user, prov(path).DELETE)

def _data_request(user, method):
	res = method(data=bottle.request.body.read(), headers=dict(bottle.request.headers), cookies=bottle.request.cookies)
	return response(user, res)

