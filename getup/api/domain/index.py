# -*- coding: utf-8 -*-

from bottle import request
from getup.response import Response
from getup.provider import OpenShift
from getup.api import Domain, App

def get(user_name, domain_name=None):
	provider = OpenShift('spinolacastro@gmail.com', 'kgb8y2k;.', default_domain='spinolacastro')
	if domain_name is None:
		domains = [ Domain(domain['id']) for domain in provider.list_domains() ]
		return Response(domains)

	apps = []
	for app in provider.list_apps(domain_name):
		apps.append(App(name=app['name'], url=app['app_url'], framework=app['framework'], git_url=app['git_url']))
	return Response(Domain(domain_name, apps=apps))
