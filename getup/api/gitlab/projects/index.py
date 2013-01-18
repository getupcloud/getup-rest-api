# -*- coding: utf-8 -*-

import bottle
from getup import aaa, gitlab, util
from getup import gitlab
from getup.response import response

@aaa.authoritative_user
@gitlab.api
def post(user, api, path):
	url = api(path)
	return _request(user, url.POST)

@aaa.authoritative_user
@gitlab.api
def delete(user, api, path):
	url = api(path)
	return _request(user, url.DELETE)

def _request(user, method, body=None):
	res = method(data=body or bottle.request.body.read(-1), headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	return response(user, res)
