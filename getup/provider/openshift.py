# -*- coding: utf-8 -*-

import bottle
from base import Provider, Hammock
from error import ProviderError
from app import App
from getup import http, response

app = bottle.default_app()

class OpenShift(Provider):
	def __init__(self, user, default_domain=None):
		Provider.__init__(self,
			name='OpenShift',
			base_url='https://' + app.config.provider['openshift']['hostname'].rstrip('/'),
			auth=(user['email'], user['authentication_token']))
		self.default_domain = default_domain

	def version(self):
		return self.api.api.GET(verify=False).json.get('version')

	def __call__(self, path):
		return self.api(path if path else '')

	def get_dom(self, name, **kvargs):
		return self.api.broker.rest.domains(name).GET(verify=False, **kvargs)

	def get_app(self, domain, name, **kvargs):
		return self.api.broker.rest.domains(domain).applications(name).GET(verify=False, **kvargs)

	def add_key(self, name, type, content, **kvargs):
		return self.api.broker.rest.user.keys.POST(verify=False, data={'name': name, 'type': type, 'content': content}, **kvargs)

	def del_key(self, name, **kvargs):
		return self.api.broker.rest.user.keys(name).DELETE(verify=False, **kvargs)

"""
	#
	# Domains
	#
	@property
	def domains(self):
		'''Retrieve all domains.
		prv = Provider(...)
		dom_list = prv.domains
		type(dom_list) == list
		'''
		return self._get_domains()

	def _get_domains(self):
		return [ Domain(self.api, dom) for dom in self.api.domains.GET() ]

	def __getitem__(self, name):
		'''Retrieve domains by name.
		prv = Provider(...)
		dom1 = prv['dom1']
		'''
		return self._get_domain(name)

	def _get_domain(self, name):
		return Domain(self.api, self.api.domains(name).GET())

	def create_domain(self, name):
		'''Create a new domain. Returns a Domain instance or raise on error.
		'''
		res = self.api.domains.POST(verify=False, data={'id': name})
		if res.ok:
			return Domain(self. api, res)
		errors = {
			422: (response.ResponseConflict, 'Domain already exists: %(resource)s'),
			409: (response.ResponseConflict, 'User already has a domain' ),
		}
		raise error.make(res, errors, resource=name)

	def delete_domain(self, name):
		res = self.api.domains(name).DELETE(verify=False, data={'force': False})
		return res, res.json
		#self.assert_response(res, [200, 204])

	#
	# Apps
	#
	def list_apps(self, domain):
		return self.api.domains(domain).applications.GET()
		return [ App(self.api, app) for app in self.api.domains(domain).applications.GET().json['data'] ]

	def get_app(self, domain, name):
		res = self.api.domains(domain).applications(name).GET()
		if not res.ok:
			raise error.ProviderError.make(res)
		return App(self.api, res)

	def create_app(self, domain, name, framework):
		domain = domain or self.default_domain
		assert domain, 'missing domain name (no default value)'

		try:
			self.get_domain(domain)
		except:
			self.create_domain(domain)

		params = {
			'name': name,
			'cartridge': framework,
			'scale': True,
		}
		res = self.api.domains(domain).applications.POST(verify=False, data=params)
		if res.ok:
			return App(self.api, res)
		errors = {
			422: (response.ResponseConflict, 'Application already exists'),
			201: response.ResponseBadRequest,
		}
		raise provider_error(res, errors, domain_id=domain, name=name)

	def set_app(self, domain, name, cartridge, scale_min=None, scale_max=None):
		params = {}
		if scale_min is not None:
			params['scales_from'] = scale_min
		if scale_max is not None:
			params['scales_to'] = scale_max

		if params:
			return self.api.domains(domain).applications(name).cartridges(cartridge).PUT(data=params)

	def scale_app(self, domain, name, to):
		return self._get_app(domain=domain, name=name)

	def delete_app(self, domain, name):
		domain = domain or self.default_domain
		assert domain, 'missing domain name (no default value)'

		res = self.api.domains(domain).applications(name).DELETE(verify=False)
		if res.ok:
			return None
		print res
		errors = {
			404: (response.ResponseNotFound, 'Application not found'),
			201: response.ResponseBadRequest,
		}
		raise provider_error(res, errors, domain_id=domain, name=name)
"""
