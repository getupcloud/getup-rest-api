# -*- coding: utf-8 -*-

import bottle
from getup import aaa, gitlab, util
from getup import gitlab
from getup.response import response

def post(path):
	print bottle.request.params.keys()
	print bottle.request.params.values()
	res = gitlab.session(email=bottle.request.params['email'], password=bottle.request.params['password'])
	return response(None, res)
