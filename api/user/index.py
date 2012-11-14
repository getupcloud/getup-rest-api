# -*- coding: utf-8 -*-

from bottle import request
from response import Response

def get(name=None):
	if name is not None:
		return Response({'username':name})
	else:
		return Response([
				{'username':'john'},
				{'username':'jerry'},
				{'username':'jenny'},
			])

def post(**kvargs):
	return Response()
