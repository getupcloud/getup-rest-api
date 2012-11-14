from .iass import IaaS
from .app import App

class OpenShift(IaaS):
	def __init__(self, username, password, default_domain=None):
		IaaS.__init__(self, name='OpenShift',
			base_url='https://openshift.redhat.com/broker/rest',
			auth=(username, password))
		self.default_domain = default_domain

	def version(self):
		#print '? version'
		if 'api' not in self._cached:
			self._cached['api'] = self._api.api.GET()
		return self._cached['api'].json.get('version')

	def apps(self):
		#print '? apps'
		return [ App(name=app['name'], url=app['app_url'], framework=app['framework'], git_url=app['git_url'])
			for app in self._list_apps() ]

	def _list_domains(self):
		#print '?? domain'
		if 'domains' not in self._cached:
			self._cached['domains'] = self._api.domains.GET()
		return self._cached['domains'].json.get('data')

	def _list_apps(self):
		#print '?? apps'
		if 'apps' not in self._cached:
			self._cached['apps'] = []
		for domain in self._list_domains():
			apps = self._api.domains(domain['id']).applications.GET().json['data']
			map(self._cached['apps'].append, apps)
		return self._cached['apps']

	def _validate(self, response, statuses=[200]):
		assert response.status_code in statuses, 'invalid response: %s %s: %s %s' % (
			response.status_code, response.reason, response.request.method, response.url)

	def _new_domain(self, name):
		print '++ domain(%s)' % name
		res = self._api.domains.POST(data={'id': name})
		self._validate(res, [200, 422])
		self.refresh('domains')

	def new_app(self, name, framework, domain=None):
		print '+ app(%s, %s, %s)' % (name, framework, domain)
		domain = domain or self.default_domain
		assert domain, 'missing domain name (no default value)'
		if 'domains' in self._cached:
			if domain not in [ dom['id'] for dom in self._cached['domains'].json.get('data') ]:
				self._new_domain(domain)
		else:
			self._new_domain(domain)
		res = self._api.domains(domain).applications.POST(data={'name': name, 'cartridge': framework})
		self._validate(res, [200, 201])
		self.refresh('apps')
		return res.json.get('data')


