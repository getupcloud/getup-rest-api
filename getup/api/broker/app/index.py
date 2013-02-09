# -*- coding: utf-8 -*-

import os
import bottle
from getup import aaa, provider, util
from getup.response import response

app = bottle.default_app()

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	res = prov(path).POST(data=bottle.request.body, headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	if res.ok:
		fields = [ 'creation_time', 'gear_count', 'embeded', 'name', 'domain_id' ]
		app_data = dict([ tuple(i, res.json['data'].get(i)) for i in fields ])
		aaa.create_app(user, app_data)
	return response(user, res)

@aaa.authoritative_user
@provider.provider
def delete(user, prov, path):
	res = prov(path).DELETE(headers=util.filter_headers(['host']), cookies=bottle.request.cookies)
	if res.ok:
		fields = [ 'creation_time', 'gear_count', 'embeded', 'name', 'domain_id' ]
		app_data = dict([ tuple(i, res.json['data'].get(i)) for i in fields ])
		aaa.create_app(user, app_data)
	return response(user, res)
