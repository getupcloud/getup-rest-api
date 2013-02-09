# -*- coding: utf-8 -*-

import bottle
from getup import aaa, gitlab, util
from getup import gitlab
from getup.response import response

@gitlab.api
def post(api, path):
	res = api(path).POST(data=body or bottle.request.body.read(-1), headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	return response(None, res)
