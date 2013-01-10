# -*- coding: utf-8 -*-

from response import Exposable

class BaseModel(dict, Exposable):
	def __init__(self, *vargs, **kvargs):
		dict.__init__(self, **kvargs)
		Exposable.__init__(self)
		_fields = {}
		for v in vargs:
			try:
				_fields.update(filter(lambda i: i[0] in self.expose, v.iteritems()))
			except AttributeError:
				_fields.update(filter(lambda i: i[0] in self.expose, zip(v.iterkeys(), v.itervalues())))
		_fields.update(filter(lambda i: i[0] in self.expose, kvargs.iteritems()))
		self.update(_fields)

		for k, v in _fields.iteritems():
			dict.__setattr__(self, k, v)

class Status(BaseModel):
	expose = [
		'database',
		'webgit',
	]
	def __init__(self, config):
		BaseModel.__init__(self, self._filter(config))

	def _filter(self, config):
		cfg = {}
		mask = [ 'pass', 'passwd', 'password', 'token', 'key', 'secret' ]
		exclude = [ 'engine', 'user' ]
		for k, v in config.iteritems():
			if k in exclude:
				continue
			elif isinstance(v, dict):
				cfg[k] = self._filter(v)
			else:
				cfg[k] = '***' if k in mask else v
		return cfg

class User(BaseModel):
	expose = [
#		'id',
		'name',
		'email',
		'created_at',
		'keys',
#		'admin',
#		'blocked',
#		'authentication_token',
	]
	def __init__(self, *vargs, **kvargs):
		BaseModel.__init__(self, *vargs, **kvargs)

class Key(BaseModel):
	expose = [
#		'id',
		'created_at',
		'updated_at',
		'key',
		'title',
		'identifier',
	]
	def __init__(self, *vargs, **kvargs):
		BaseModel.__init__(self, *vargs, **kvargs)

class Domain(BaseModel):
	expose = [
		'id',
		'suffix',
	]
	def __init__(self, *vargs, **kvargs):
		BaseModel.__init__(self, *vargs, **kvargs)

'''
class App(BaseModel):
	fields = [
		'name',
		'app_url',
		'framework',
		'git_url',
		'status',
		'domain_id',
		'instances',
	]
	def __init__(self, *vargs, **kvargs):
		BaseModel.__init__(self, App.fields, *vargs, **kvargs)
'''
