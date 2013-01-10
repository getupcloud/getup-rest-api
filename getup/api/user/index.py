# -*- coding: utf-8 -*-

import bottle
from getup import aaa, codec
from getup import database, gitlab, util
from getup.response import response

app = bottle.app()

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
@gitlab.api
def delete(user, api, path):
	return _data_request(user, api(path).DELETE)

def _data_request(user, method):
	res = method(data=bottle.request.body.read() or '', headers=util.filter_headers(), cookies=bottle.request.cookies)
	return response(user, res)

