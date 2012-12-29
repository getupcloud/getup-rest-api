# -*- coding: utf-8 -*-

class BaseModel(dict):
	def __init__(self, allow_fields, *vargs, **kvargs):
		dict.__init__(self, **kvargs)
		for v in vargs:
			try:
				self.update(filter(lambda i: i[0] in allow_fields, v.iteritems()))
			except AttributeError:
				self.update(filter(lambda i: i[0] in allow_fields, zip(v.iterkeys(), v.itervalues())))

	def __getattr__(self, name):
		if name in self:
			return self.get(name)
		raise AttributeError(name)

class User(BaseModel):
	fields = [
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
		BaseModel.__init__(self, User.fields, *vargs, **kvargs)

class Key(BaseModel):
	fields = [
#		'id',
		'created_at',
		'updated_at',
		'key',
		'title',
		'identifier',
	]
	def __init__(self, *vargs, **kvargs):
		BaseModel.__init__(self, Key.fields, *vargs, **kvargs)

'''
class Domain(dict):
	def __init__(self, domain_name, **kvargs):
		dict.__init__(self, domain_name=domain_name, **kvargs)
		self['domain_name'] = domain_name

class App(dict):
	def __init__(self, name, url, framework, git_url):
		self['name'] = name
		self['url'] = url
		self['framework'] = framework
		self['git_url'] = git_url
		self['status'] = {}
'''
