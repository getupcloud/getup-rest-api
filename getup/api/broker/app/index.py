# -*- coding: utf-8 -*-

import os, urllib
import bottle
from getup import aaa, provider
from getup.response import response

app = bottle.default_app()

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	res = prov(path).POST(data=bottle.request.body.read(), headers=dict(bottle.request.headers), cookies=bottle.request.cookies)

	# register gitlab pubkey into openshift application
	with open(os.path.expanduser(app.config.webgit['pubkey_file'])) as pubkey:
		key = dict(zip(['type', 'content', 'name'], pubkey.readline().split()))
		key['content'] = urllib.quote(key['content'])
		key['name'] = 'getupcloud'
	r = prov.broker.rest.user.keys.POST(data=key)
	if not r.ok:
		print 'error registering gitlab public key: %s - %s - \n%s' % (r, r.request.body, r.request.headers)

	return response(user, res)
