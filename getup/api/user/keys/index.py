# -*- coding: utf-8 -*-

import bottle
from getup import aaa, codec, model, proto
from getup import database, response, gitlab

@aaa.authoritative_user
@gitlab.api
def post(user, api, path):
	# dont need to post key to openshift beacuse gitlab's
	# system hook will do it for us
	res = api.add_key(bottle.request.body.read(-1), headers=util.filter_headers())
	return None

def post(user, title, content, *vargs, **kvargs):
	key = model.Key(title=title, key=content['key'])
	ret = gitlab.Gitlab(user['authentication_token']).user.keys.POST(data=key)
	if ret.status_code != 201:
		return response.ResponseBadRequest()
	try:
		key = [ model.Key(k) for k in database.keys(user, key=key.key) ]
	except:
		pass
	return response.ResponseCreated(key)

@aaa.authoritative_user
def delete(user, keyname, keyident=None):
	ids = { 'title': keyname }
	if keyident is not None:
		ids['identifier'] = keyident
	keys = database.keys(user, **ids).fetchall()
	if not keys:
		return response.ResponseNotFound()
	elif len(keys) > 1:
		return response.ResponseMultipleChoices([ model.Key(k) for k in keys ])
	key = keys[0]
	ret = gitlab.Gitlab(user['authentication_token']).user.keys(key['id']).DELETE()
	if ret.status_code != 200:
		return response.ResponseBadRequest()
	return response.ResponseOK()
