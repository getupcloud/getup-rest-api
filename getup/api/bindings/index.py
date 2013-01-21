# -*- coding: utf-8 -*-

from getup import aaa, provider, codec, gitlab
from getup.response import response

def get():
	return response.ResponseOK()

@aaa.authoritative_user
@provider.provider
@gitlab.api
def post(user, prov, api):
	try:
		params = bottle.request.params
		domain, name, project = params['domain'], params['name'], params['project']
	except KeyError:
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)
	res = prov.get_app(domain=params['domain'], name=params['name'])
	data = res.json['data']
	gear = data['git_url']
	return gear
