# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider, gitlab, util
from getup.response import response

@aaa.authoritative_user
@provider.provider
@gitlab.api
def post(user, prov, api, path):
	# post key to openshift
	res = prov.add_key(headers=bottle.request.headers, cookies=bottle.request.cookies, **dict(bottle.request.forms))

	# post key to gitlab
	# this will trigger a system hook, wich in turn will call us again on /gitlab/hook
	title = bottle.request.params.name,
	key = '%s %s %s' % (bottle.request.forms.type, bottle.request.params.content, user.email),
	res_api = api.add_key(title=title, key=key, headers=util.filter_headers())
	if not res_api.ok:
		print 'WARNING: Unable to post user key to gitlab: status=%s, key=%s %s' % (res_api.status_code, title, key)

	# return openshift status only
	return response(user, res)

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

