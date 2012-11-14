from hammock import Hammock
from .app import App

class IaaS:
	def __init__(self, name, base_url, auth, accept='application/json'):
		self._name = name
		self._base_url = base_url
		self._auth = auth
		headers = { 'accept': accept }
		self._api = Hammock(base_url, auth=auth, headers=headers)
		self._cached = dict()

	def __getattr__(self, name):
		return getattr(self._api, name)

	def refresh(self, what=None):
		if what and what in self._cached:
			self._cached.pop(what)
		elif what:
			self._cached = dict()

	def version(self):
		return None

	def apps(self):
		return App()

	def new_app(self, name, framework, **kvargs):
		return False

