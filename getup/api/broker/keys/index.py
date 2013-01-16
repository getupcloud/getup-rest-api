# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider, gitlab, util
from getup.response import response

@aaa.authoritative_user
@provider.provider
@gitlab.api
def post(user, prov, api, path):
	cookies = bottle.request.cookies
	res = prov.add_key(path=path, body=bottle.request.body.read(), headers=dict(bottle.request.headers), cookies=dict(cookies))
	print 'BROKER:', res, res.text
	if res.ok:
		body = {
			'title': bottle.request.params.name,
			'key': '%s %s' % (bottle.request.params.type, bottle.request.params.content),
		}
		api_res = api.add_key(body=body, headers=util.filter_headers(), cookies=cookies)
		print 'GITLAB:', api_res, api_res.text
		if not api_res.ok:
			print 'WARNING: Unable to post user key to gitlab:', api_res.status_code
	return res

@aaa.authoritative_user
@provider.provider
def put(user, prov):
	return _data_request(user, prov(path).PUT)

@aaa.authoritative_user
@provider.provider
def delete(user, prov):
	return _data_request(user, prov(path).DELETE)

def _data_request(user, method, body=None):
	res = method(data=body or bottle.request.body.read(), headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

