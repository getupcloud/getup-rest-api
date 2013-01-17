# -*- coding: utf-8 -*-

import bottle
from getup import aaa, codec, provider
from getup import database, gitlab, util
from getup.response import response

def post():
	# Post key to openshift.
	# If it was triggered by gitlab's system hooks (web or /api), broker will return OK.
	# If it was triggered by api (/broker), broker will return 409-120/121 since /broker
	# already posted the key (not a big concern right now).
	event = bottle.request.json
	if event['event_name'] == 'key_save':
		user = database.user(email=event['owner_email'])
		prov = provider.OpenShift(iusername=user['email'], password=user['authentication_token'])
		try:
			type, content, _ = event['key'].split()
		except:
			type, content = event['key'].split()
		res = prov.add_key(name=event['title'], type=type, content=key)
	else:
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)
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

