from provider import Provider
from api import App

class OpenShift(Provider):
	def __init__(self, username, password, default_domain=None):
		Provider.__init__(self, name='OpenShift',
			base_url='https://openshift.redhat.com/broker/rest',
			auth=(username, password))
		self.default_domain = default_domain

	def version(self):
		return self._api.api.GET().json.get('version')

	#
	# Domains
	#
	def list_domains(self):
		req = self._api.domains
		return req.GET().json.get('data')

	def get_domain(self, name):
		res = self._api.domains(name).GET()
		self.assert_response(res, [200])
		return res.json.get('data')

	def create_domain(self, name):
		res = self._api.domains.POST(data={'id': name})
		self.assert_response(res, [200, 422])

	#
	# Apps
	#
	def list_apps(self, domain):
		res = self._api.domains(domain).applications.GET()
		self.assert_response(res, [200])
		return res.json['data']

	def get_app(self, domain, name):
		res = self._api.domains(domain).applications(name).GET()
		self.assert_response(res, [200])
		return res.json['data']

	def create_app(self, domain_name, app_name, framework):
		domain = domain_name or self.default_domain
		assert domain, 'missing domain name (no default value)'

		try:
			self.get_domain(domain)
		except:
			self.create_domain(domain)

		params = {'name':app_name}
		if framework:
			params['cartridge'] = str(framework)
		res = self._api.domains(domain).applications.POST(data=params)
		self.assert_response(res, [200, 201])
		return res.json.get('data')

	def delete_app(self, domain_name, app_name):
		domain = domain_name or self.default_domain
		assert domain, 'missing domain name (no default value)'

		app = self.get_app(domain_name, app_name)
		res = self._api.domains(domain).applications(app_name).DELETE()
		self.assert_response(res, [200, 204])
		return app
