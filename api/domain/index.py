# -*- coding: utf-8 -*-

from bottle import request
from response import Response

def get(domain):
	return Response({'domain':domain})

def post(**kvargs):
	return Response()
