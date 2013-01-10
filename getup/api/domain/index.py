# -*- coding: utf-8 -*-

from getup import aaa, model, response, provider

@aaa.authoritative_user
@provider.provider
def get(user, prov, domain=None):
	if domain is None:
		res, domains = prov.list_domains()
		return response.ResponseOK([ model.Domain(domain) for domain in domains ])
	res, dom = prov.get_domain(domain)
	if res.status_code != 200:
		return response.ResponseNotFound([ model.Domain(id=domain) ])
	res, apps = prov.list_apps(domain)
	apps = [ model.App(app, health_check=prov.health_check(app)) for app in apps ]
	dom = model.Domain(dom)
	return response.ResponseOK({'apps':apps, 'domain':dom})

@aaa.authoritative_user
@provider.provider
def post(user, prov, domain):
	assert domain, 'missing domain name'
	res, dom = prov.create_domain(domain)
	if res.status_code == 201:
		return response.ResponseCreated([ model.Domain(dom) ])
	elif res.status_code == 422:
		return response.ResponseConflict([ model.Domain(id=domain) ])
	return response.ResponseBadRequest(res)

@aaa.authoritative_user
@provider.provider
def delete(user, prov, domain):
	res, dom = prov.delete_domain(domain)
	if res.status_code == 404:
		return response.ResponseNotFound([ model.Domain(id=domain) ])
	elif res.status_code != 204:
		return response.ResponseConflict(res)
	return response.ResponseOK([ model.Domain(id=domain) ])
