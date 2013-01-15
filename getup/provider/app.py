# -*- coding: utf-8 -*-

from hammock import Hammock
from getup import http, response
import error

def _get_attr_or_item(obj, name):
	'''Returns obj.name, otherwise returns obj[name] or
	raises AttributeError if not found.
	'''
	try:
		return getattr(obj, name)
	except:
		try:
			return obj[name]
		except KeyError:
			raise AttributeError(name)

def provider_data(obj, *validate_fields):
	'''Returns provider application data from obj. The returned content
	is requests specific, i.e. if obj is the result of an app-request,
	this function returns the app 'data' field.

	If supplied, validate_fields contains a list of names that must
	exists in obj. If any is missing, raise ValueError.
	'''
	try:
		return obj.json['data']
	except (KeyError, AttributeError):
		if not (isinstance(obj, dict) and all(map(lambda x: x in obj, validate_fields))):
			raise ValueError("Invalid object instance")
		return obj

class NullDomain(response.Exposable):
	_expose = [
		'id',
	]
	def __init__(self, id):
		self.id = id

class Domain(response.Exposable):
	'''Maps a provider domain into a manageable object.
	'''
	_expose = [
		'id',
		'suffix',
	]
	def __init__(self, api, dom):
		self.api = api
		self.dom = provider_data(dom, 'id')

	def __repr__(self):
		try:
			return '<Domain(dom=%r)>' % {'id':self.id, 'suffix': self.suffix}
		except AttributeError:
			return '<Domain(dom=%r)>' % {'id':self.id}

	def __getattr__(self, name):
		return _get_attr_or_item(self.dom, name)

	@property
	def apps(self):
		'''Retrieve all apps from this domain.
			dom = Domain(...)
			app_list = dom.apps
			type(app_list) == list
		'''
		return self._get_apps()

	def _get_apps(self):
		return [ App(self.api, app) for app in self.api.domains(self.id).applications.GET() ]

	def __getitem__(self, name):
		'''Retrieve apps by name.
			dom = Domain(...)
			app1 = dom['app1']
		'''
		return self._get_app(name)

	def _get_app(self, name):
		res = self.api.domains(self.id).applications(name).GET()
		if not res.ok:
			raise error.DomainError.make(res)
		return App(self.api, res)

	def create_app(self, name, framework):
		'''Create a new app. Return an App instance or raise on error.
		'''
		params = {
			'name': name,
			'cartridge': framework,
			'scale': True,
		}
		res = self.api.domains(self.id).applications.POST(data=params)
		if res.ok:
			return App(self.api, res)
		raise error.AppError.make(res)

	def delete_app(self, app):
		'''Deletes an app from domain. Raise on error.
		'''
		try:
			res = self.api.domains(self.id).applications(app.name).DELETE()
		except AttributeError:
			res = self.api.domains(self.id).applications(app).DELETE()

		if res.ok:
			return

		errors = {
			404: (response.ResponseNotFound, 'Application not found'),
			201: response.ResponseBadRequest,
		}
		raise provider_error(res, errors, domain_id=domain, name=name)

#
# Applications
#
class NullApp(response.Exposable):
	_expose = [
		'name',
		'domain_id',
	]
	def __init__(self, domain, name):
		self.domain_id = domain
		self.name  = name

class App(response.Exposable):
	'''Maps a provider application into a manageable object.
	'''
	_expose = [
		'name',
		'domain_id',
		'app_url',
		'framework',
		'git_url',
		'instances',
		'status',
	]

	def __init__(self, api, app):
		self.api = api
		self.app = provider_data(app, 'name')
		self._cartridge = None

	def __getattr__(self, name):
		return _get_attr_or_item(self.app, name)

	def __getitem__(self, name):
		if name == 'cartridge':
			return self._get_cartridge()
		elif name == 'status':
			return self._get_status()
		return self.app[name]

	def __repr__(self):
		return '<App(app=%r)>' % {'name':self.name, 'domain_id':self.domain_id}

	def configure(self, scale_min=None, scale_max=None):
		params = {}
		if scale_min is not None and scale_min > -1 and self.instances['min'] != scale_min:
			params['scale_min'] = scale_min
		if scale_max is not None and scale_max > -1 and self.instances['max'] != scale_max:
			params['scale_max'] = scale_max

		if not params:
			return None
		res = self.api.domains(domain).applications(name).cartridges(cartridge).PUT(data=params)
		if not res.ok:
			raise error.AppError(res, resource=params)

	@property
	def cartridge(self):
		return self._get_cartridge()

	def _get_cartridge(self):
		if self._cartridge is None:
			self._cartridge = self.api.domains(self.domain_id).applications(self.name).cartridges.GET(self.framework)
			if not self._cartridge.ok:
				return None
		return self._cartridge.json['data']

	@property
	def instances(self):
		c = self._get_cartridge()
		return {
			'run': self.gear_count,
			'min': c['scales_from'],
			'max': c['scales_to'],
		}

	def scale(to):
		if to.lower() == 'up':
			offset = 1
		elif to.lower() == 'down':
			offset = -1
		else:
			offset = int(to)

		if offset > 0:
			_range = xrange(0, offset)
			event = { 'event': 'scale-up'}
		else:
			_range = xrange(offset, 0)
			event = { 'event': 'scale-down'}

		for i in _range:
			res = self.api.domains(domain_id).applications(name).events.POST(data=event)
			if res.status_code != 200:
				raise error.AppScaleError(self)
		return True

	@property
	def status(self):
		return self._get_status()

	def _get_status(self):
		url = Hammock(self.app_url.rstrip('/'))(self.health_check_path.lstrip('/'))
		try:
			res = url.GET(verify=False)
			code = res.status_code
		except:
			code = 500
		message = http.responses(code)
		return {'health_check_url': url, 'code': code, 'message': message}
