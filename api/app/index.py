# -*- coding: utf-8 -*-

from bottle import request
from response import Response
from app import App

def get(domain, name):
	username = 'john'
	app = App(name=name, domain=domain, url='http://%s-%s.getupcloud.com' % (name, domain), framework='php-5.2', git_url='ssh://%s@git.getupcloud.com/example' % username)
	return Response(app)

def post(**kvargs):
	return Response()
