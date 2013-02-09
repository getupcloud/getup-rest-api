# -*- coding: utf-8 -*-

import os
import bottle
from getup import aaa, provider
from getup.response import response

app = bottle.default_app()

@aaa.authoritative_user
@provider.provider
def post(user, prov, path):
	res = prov(path).POST(data=bottle.request.body.read(), headers=dict(bottle.request.headers), cookies=bottle.request.cookies)
	return response(user, res)
