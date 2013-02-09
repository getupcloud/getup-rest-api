# -*- coding: utf-8 -*-

import bottle
from getup import aaa, gitlab, util
from getup import gitlab
from getup.response import response

def post():
	res = gitlab.session(body=bottle.request.body.read())
	return response(None, res)
