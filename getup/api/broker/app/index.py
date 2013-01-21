# -*- coding: utf-8 -*-

import os, urllib
import bottle
from getup import aaa, provider
from getup.response import response

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	res = prov(path).POST(data=bottle.request.body.read(), headers=dict(bottle.request.headers), cookies=bottle.request.cookies)

	# register gitlab pubkey into openshift application
	with open(os.path.expanduser(app.config.webgit['pubkey_file'])) as pubkey:
		key = dict(zip(['type', 'content', 'name'], map(urllib.quote, pubkey.readline().split())))
	if not prov.broker.rest.user.keys.POST(data=key).ok:
		print 'error registering gitlab public key:', key

	return response(user, res)
