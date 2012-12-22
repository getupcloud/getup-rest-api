# -*- coding: utf-8 -*-

from bottle import request
from getup.response import Response, ResponseCreated
#from provider import OpenShift
from getup.api import User

def get(user_id=None):
	if user_id is None:
		return Response([ User(name) for name in ('john', 'ringo', 'paul', 'george') ])
	return Response(User(user_id))

def post(user_id):
	base_url = '%s://%s/user' % request.urlparts[0:2]
	url = '%s/%s' % (base_url, user_id)
	return ResponseCreated(User(user_id, location={'method':'GET', 'url':url}))
