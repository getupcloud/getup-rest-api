# -*- coding: utf-8 -*-

import bottle
from getup import aaa, codec, provider
from getup import database, gitlab, util
from getup.response import response

@aaa.authoritative_user
@gitlab.api
def get(user, api, path):
	url = api(path)
	res = url.GET(headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

@aaa.authoritative_user
@gitlab.api
def post(user, api, path):
	return _data_request(user, api(path).POST)

@aaa.authoritative_user
@gitlab.api
def put(user, api, path):
	return _data_request(user, api(path).PUT)

@aaa.authoritative_user
@provider.provider
@gitlab.api
def delete(user, prov, api, keyid, path):
	#TODO: gitlab system hook is not calling us here
	# first delete key from openshift
	keys = database.keys(user, id=keyid)
	if keys:
		for key in keys:
			res = prov.del_key(key['title'])
			if not res.ok:
				print 'WARNING: Unable to delete user key from openshift: status=%s, key[%i]=%s %s' % (res.status_code, key['id'], key['title'], key['key'])
	# then from gitlab
	return _data_request(user, api(path).DELETE)

def _data_request(user, method):
	res = method(data=bottle.request.body, headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

