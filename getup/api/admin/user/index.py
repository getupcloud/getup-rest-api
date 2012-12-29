# -*- coding: utf-8 -*-

from bottle import request
from getup.response import ResponseOK, ResponseCreated
#from provider import OpenShift
from getup.model import User
from getup import gitlab

def get(user_name=None):
	if user_name:
		return ResponseOK(User(user_id))
	return ResponseOK([ User(user) for user in gitlab.user() ])

def post (user_id):
	raise NotImplemented('post /admin/user')
	base_url = '%s://%s/user' % request.urlparts[0:2]
	url = '%s/%s' % (base_url, user_id)
	return ResponseCreated(User(user_id, location={'method':'GET', 'url':url}))

def put(user_id):
	raise NotImplemented('put /admin/user')
	base_url = '%s://%s/user' % request.urlparts[0:2]
	url = '%s/%s' % (base_url, user_id)
	return ResponseCreated(User(user_id, location={'method':'GET', 'url':url}))

def delete(user_name=None):
	raise NotImplemented('delete /admin/user')
