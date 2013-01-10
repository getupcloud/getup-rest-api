# -*- coding: utf-8 -*-

import bottle
from getup import aaa, model, response, provider, codec
from getup.provider import error
from getup.provider.app import NullApp

@aaa.authoritative_user
@provider.provider
def get(user, prov, domain, name=None):
	'''List one or all user apps
	'''
	if name is None:
		return prov.list_apps(domain)

	app = prov.get_app(domain, name)
	if not app:
		return response.ResponseNotFound(NullApp(domain, name))
	return response.ResponseOK(app)

@aaa.authoritative_user
@codec.decoder(codec.json, codec.form_urlencoded)
@codec.parse_params('framework', scale_min=-1, scale_max=-1)
@provider.provider
def post(user, prov, domain, name, content, params):
	'''Create an app within a domain.
	'''
	app = prov.create_app(domain, name, params['framework'])
	app.configure(scales_min=params['scale_min'], scale_max=params['scale_max'])
	app = prov.get_app(domain, name)
	app.config(scale_min=params['scale_min'], scale_max=params['scale_max'])
	return response.ResponseCreated( model.App(app, health_check=prov.health_check(app)) )

def _set_app_scale_limits(prov, app, scale_min, scale_max):
	limits = {}
	if scale_min > -1 and app['instances']['min'] != scale_min:
		limits['scale_min'] = scale_min
	if scale_max > -1 and app['instances']['max'] != scale_max:
		limits['scale_max'] = scale_max
	return prov.set_app(app['domain_id'], app['name'], app['framework'], **limits)

@aaa.authoritative_user
@provider.provider
def delete(user, prov, domain, name):
	'''Delete a single app
	'''
	try:
		return response.ResponseOK(prov.delete_app(domain, name))
	except ProviderError, ex:
		return ex.response
