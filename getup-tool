#!/usr/bin/env python

import os, sys

#import argparse
#parser = argparser.ArgumentParser(description='GetUp Cloud - command line tool')
#parser.add_argument()

if len(sys.argv) not in [1, 3, 4]:
	argv0 = os.path.basename(sys.argv[0])
	print 'GetUp Cloud -- command line tool'
	print
	print 'Usage:'
	print ' List applications'
	print '   $', argv0
	print
	print ' Create application'
	print '   $', argv0, 'app-name framework [domain]'
	print
	sys.exit(1)

################################################################

from hammock import Hammock
from collections import namedtuple
import git

################################################################

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
		return tuple()

	def new_app(self, name, framework, **kvargs):
		return False

################################################################

App = namedtuple('App', 'name url framework git_url')

################################################################

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

################################################################

class Repo:
	class Progress(git.remote.RemoteProgress):
		NAMES = {
			git.remote.RemoteProgress.COUNTING: 'counting',
			git.remote.RemoteProgress.COMPRESSING: 'compressing',
			git.remote.RemoteProgress.WRITING: 'writing',
			git.remote.RemoteProgress.RECEIVING: 'receiving',
			git.remote.RemoteProgress.RESOLVING: 'resolving',
		}

		def update(self, op_code, cur_count, max_count, message):
			if (op_code & self.STAGE_MASK) == self.BEGIN:
				print 'git:  ', self.NAMES[op_code & self.OP_MASK]
				#sys.stdout.flush()
			#print '>> %s %s/%s %s' % (op_code, cur_count, max_count, message)

	def __init__(self, app):
		name = app['name']
		try:
			self.git = git.Repo(name)
			print '! repo(%(name)s)' % app
		except git.NoSuchPathError:
			url = app['git_url']
			print 'git: cloning'
			self.git = git.Repo.clone_from(url, name, Repo.Progress())
			print '\n+ repo(%(name)s, %(git_url)s)' % app
		self.path = self.git.working_dir

################################################################

iaas = OpenShift('spinolacastro@gmail.com', 'kgb8y2k;.', default_domain='spinolacastro')

if 3 <= len(sys.argv) <= 4:
	print 'Creating Application:'
	try:
		name, framework, domain =  sys.argv[1:]
	except:
		name, framework =  sys.argv[1:]
		domain = None
	app = iaas.new_app(name, framework, domain)
	repo = Repo(app)
	print 'New application repo: %s' % os.path.join(os.getcwd(), repo.path)
elif len(sys.argv) == 1:
	print 'Listing Applications:'
	for app in iaas.apps():
		a = app._asdict()
		print
		print '- %(name)s (%(framework)s)' % a
		print '  url: %(url)s' % a
		print '  git: %(git_url)s' % a
	print
