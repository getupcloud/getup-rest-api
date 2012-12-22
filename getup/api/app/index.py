# -*- coding: utf-8 -*-

from bottle import request
from getup.response import Response, ResponseCreated, ResponseBadRequest
from getup.provider import OpenShift
from getup.api import App

def get(user_name, domain_name, app_name):
	provider = OpenShift('spinolacastro@gmail.com', 'kgb8y2k;.', default_domain='spinolacastro')
	app = provider.get_app(domain_name, app_name)
	return Response(App(name=app['name'], url=app['app_url'], framework=app['framework'], git_url=app['git_url']))

def post(user_name, domain_name, app_name):
	provider = OpenShift('spinolacastro@gmail.com', 'kgb8y2k;.', default_domain='spinolacastro')
	app = provider.create_app(domain_name, app_name, request.params.framework)
	return ResponseCreated(App(name=app['name'], url=app['app_url'], framework=app['framework'], git_url=app['git_url']))

def delete(user_name, domain_name, app_name):
	provider = OpenShift('spinolacastro@gmail.com', 'kgb8y2k;.', default_domain='spinolacastro')
	app = provider.delete_app(domain_name, app_name)
	return Response(App(name=app['name'], url=app['app_url'], framework=app['framework'], git_url=app['git_url']))
