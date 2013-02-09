# -*- coding: utf-8 -*-

import os
import bottle
from getup import aaa, provider
from getup.response import response

app = bottle.app()

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	url = prov(path)
	res = url.POST(data=bottle.request.body, headers=dict(bottle.request.headers), cookies=bottle.request.cookies)

	try:
		# register gitlab pubkey into openshift application
		with open(os.path.expanduser(app.config.webgit['pubkey_file'])) as pubkey:
			# dont re-post if key is already there
			current_key = prov.broker.rest.user.keys('getupcloud').GET().json
			key = dict(zip(['type', 'content'], pubkey.readline().split()), name='getupcloud')
			if current_key['content'] != key['content']:
				r = prov.broker.rest.user.keys.POST(data=key)
				if r.status_code != 409 and not r.ok:
					print 'error registering pubkey "getupcloud" into openshift application: %s' % r
	except Exception, ex:
		print 'exception registering pubkey "getupcloud" into openshift application: %s: %s' % (ex.__class__, ex)

	return response(user, res)
