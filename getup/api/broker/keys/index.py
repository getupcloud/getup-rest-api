# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider, gitlab, util, database
from getup.response import response

@aaa.authoritative_user
@provider.provider
@gitlab.api
def post(user, prov, api, path):
	# post key to openshift
	res = prov.add_key(headers=dict(bottle.request.headers), cookies=dict(bottle.request.cookies), **dict(bottle.request.params))

	# post key to gitlab
	# this will trigger a system hook, wich in turn will call us again on /gitlab/hook
	title = bottle.request.params.name
	key = '%s %s %s' % (bottle.request.params.type, bottle.request.params.content, user.email)
	res_api = api.add_key(title=title, key=key, headers=util.filter_headers())
	if not res_api.ok:
		print 'WARNING: Unable to post user key to gitlab: status=%s, key=%s %s' % (res_api.status_code, title, key)

	# return openshift status only
	return response(user, res)

# TODO
@aaa.authoritative_user
@provider.provider
def put(user, prov):
	raise NotImpementedError()
	#return _data_request(user, prov(path).PUT)

@aaa.authoritative_user
@provider.provider
@gitlab.api
def delete(user, prov, api, keyname, path):
	if keyname == 'getupcloud':
		return response(user, status=http.HTTP_FORBIDDEN)
	# first delete gitlab's key
	keys = database.keys(user, title=keyname)
	if keys:
		for key in keys:
			res = api.del_key(key['id'], headers=util.filter_headers())
			if not res.ok:
				print 'WARNING: Unable to delete user key from gitlab: status=%s, key[%i]=%s %s' % (res.status_code, key['id'], key['title'], key['key'])

	# then openshit's key
	return _data_request(user, prov(path).DELETE)

def _data_request(user, method, body=None):
	res = method(data=body or bottle.request.body.read(-1), headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

