# -*- coding: utf-8 -*-

import bottle
from getup import aaa, codec, util
from getup import database, gitlab
from getup.response import response

@aaa.authoritative_user
@gitlab.api
def get(user, api, path, userid=None):
	url = api(path)
	if userid is not None:
		url = url(user.id if user else userid)
	res = url.GET(headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

def api_for_user(api, path, userid):
	return api(path)(userid) if userid is not None else api(path)

@aaa.authoritative_user
@gitlab.api
def post(user, api, path, userid):
	return _data_request(user, api_for_user(api, path, userid).POST)

@aaa.authoritative_user
@gitlab.api
def put(user, api, path, userid):
	return _data_request(user, api_for_user(api, path, userid).PUT)

@aaa.authoritative_user
@gitlab.api
def delete(user, api, path, userid):
	#TODO: block user instead delete
	return _data_request(user, api_for_user(api, path, userid).DELETE)

def _data_request(user, method):
	res = method(data=bottle.request.body.read() or '', headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

