# -*- coding: utf-8 -*-

import os
import bottle
from getup import aaa, provider, util
from getup.response import response

app = bottle.app()

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	url = prov(path)
	res = url.POST(data=bottle.request.body, headers=util.filter_headers(['host']), cookies=bottle.request.cookies)

	# check if openshift user already has getupcloud key
	user_res = prov.broker.rest.user.keys('getupcloud').GET()
	if user_res.ok and user_res.json.get('content') == bottle.request.params.get('content'):
		return response(user, res)

	# register getupcloud key to openshift user
	with open(os.path.expanduser(app.config.webgit['pubkey_file'])) as pubkey:
		key = dict(zip(['type', 'content'], pubkey.readline().split()), name='getupcloud')
		user_res = prov.broker.rest.user.keys.POST(data=key)
		if user_res.status_code != 409 and not user_res.ok:
			print 'error registering pubkey "getupcloud" into openshift application: %s' % user_res

	return response(user, res)
