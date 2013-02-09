# -*- coding: utf-8 -*-

import bottle
from getup import aaa, gitlab, util
from getup import gitlab
from getup.response import response

@aaa.authoritative_user
@gitlab.api
def get(user, api, path):
	url = api(path)
	return _request(user, url.GET)

@aaa.authoritative_user
@gitlab.api
def post(user, api, path):
	url = api(path)
	return _request(user, url.POST)

@aaa.authoritative_user
@gitlab.api
def put(user, api, path):
	url = api(path)
	return _request(user, url.PUT)

@aaa.authoritative_user
@gitlab.api
def delete(user, api, path):
	url = api(path)
	return _request(user, url.DELETE)

def _request(user, method, body=None):
	res = method(data=body or bottle.request.body, headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	return response(user, res)
