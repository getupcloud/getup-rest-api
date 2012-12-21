# -*- coding: utf-8 -*-

version = '1.0'

class User(dict):
	def __init__(self, user_id, **kvargs):
		dict.__init__(self, user_id=user_id, **kvargs)

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

from index import *
import user
import app
import domain
