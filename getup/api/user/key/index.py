# -*- coding: utf-8 -*-

import bottle
from getup import aaa, codec, model, proto
from getup import database, response, gitlab

@aaa.authoritative_user
def get(user, keyname=None, keyident=None):
	ids = {}
	if keyname is not None:
		ids['title'] = keyname
	if keyident is not None:
		ids['identifier'] = keyident
	keys = [ model.Key(key) for key in database.keys(user, **ids) ]
	if ids and not keys:
		return response.ResponseNotFound()
	else:
		return response.ResponseOK(model.User(user, keys=keys))

@aaa.authoritative_user
@proto.content_type('application/json')
@codec.decode(codec.json)
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
