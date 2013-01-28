# -*- coding: utf-8 -*-

import bottle
from getup import database, http, aaa
from getup.response import response

def _get_user(username):
	user = database.user(email=username)
	if not user:
		raise response(user, status=http.HTTP_NOT_FOUND)
	return user

def post(username):
	user = _get_user(username)
	try:
		appname = bottle.request.params['name']
	except KeyError:
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)
	aaa.create_gear(user, appname)
	return response(user, status=http.HTTP_CREATED)

def delete(username, appname):
	user = _get_user(username)
	aaa.delete_gear(user, appname)
	return response(user, status=http.HTTP_NO_CONTENT)
