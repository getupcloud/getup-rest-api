import bottle
from abc import ABCMeta, abstractmethod
from hammock import Hammock

class Provider:
	__metaclass__ = ABCMeta

	def __init__(self, name, base_url, auth, accept='application/json'):
		self._name = name
		self._base_url = base_url
		self._auth = auth
		headers = { 'accept': accept }
		self._api = Hammock(base_url, auth=auth, headers=headers)

	def __getattr__(self, name):
		return getattr(self._api, name)

	def assert_response(self, response, statuses=[200]):
		'''Validates HTTP response from provider.
		Raises AssertionError if status code does not match any of statuses.
		'''
		if response.status_code == statuses or response.status_code in statuses:
			return True
		res = dict(
			code=response.status_code,
			reason=response.reason,
			method=response.request.method,
			url=response.url)
		raise bottle.HTTPError(status=response.status_code,
			body='invalid response: %(code)s %(reason)s: %(method)s %(url)s' % res)

	@abstractmethod
	def version(self):
		'''Return provider API version
		'''

	#
	# Domains
	#
	@abstractmethod
	def list_domains(self, **kvargs):
		'''List registered domains owned by a user.
		'''

	@abstractmethod
	def get_domain(self, name, **kvargs):
		'''Return information about a specific domain.
		'''

	@abstractmethod
	def create_domain(self, name, **kvargs):
		'''Create a new domain.
		'''

	#
	# Apps
	#
	@abstractmethod
	def list_apps(self, domain, **kvargs):
		'''List all apps owned by a user for a specific domain.
		'''

	@abstractmethod
	def get_app(self, domain, name, **kvargs):
		'''Return information about a specific app.
		'''

	@abstractmethod
	def create_app(self, domain, name, framework, **kvargs):
		'''Create a new app within a domain.
		'''

	def delete_app(self, domain_name, app_name):
		'''Delete an app.
		'''
