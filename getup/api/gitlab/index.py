# -*- coding: utf-8 -*-

import bottle
from getup import aaa, gitlab
from getup import gitlab
from getup.response import response

@aaa.authoritative_user
@gitlab.api
def get(user, api, path):
	url = api(path)
	return _request(user, url.GET)

def _request(user, method, body=None):
	res = method(data=body or bottle.request.body.read(-1), headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)
