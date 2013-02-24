# -*- coding: utf-8 -*-

from path import path as Path
from collections import defaultdict
import os
import copy

class Tree(defaultdict, object):
	def __init__(self, *va, **kva):
		super(Tree, self).__init__(*va, **kva)

	def __getattr__(self, key):
		return self[key]

	def __setattr__(self, key, value):
		self[key] = value

	# uncoment if you want print to show values only
	def __repr__(self):
		return str(dict(self))

def tree(**values):
	return Tree(tree, **values)

app_root = Path(os.environ.get('APP_ROOT', Path(__file__).dirname().dirname()))

valid_config = tree()

valid_config.database.url                = 'mysql://{username}:{password}@{hostname}/{database}?charset={charset}'
valid_config.database.config.hostname    = 'mysql.ops.getupcloud.com'
valid_config.database.config.port        = 3306
valid_config.database.config.database    = 'getup'
valid_config.database.config.username    = 'getup'
valid_config.database.config.password    = ''
valid_config.database.config.charset     = 'utf8'
valid_config.database.config.unix_socket = '/var/run/mysqld/mysqld.sock'
valid_config.database.parameters.encoding     = 'utf-8'
valid_config.database.parameters.echo         = False
valid_config.database.parameters.pool_recycle = 3600

valid_config.webgit.hostname      = 'git.ops.getupcloud.com'
valid_config.webgit.token_header  = 'Private-Token'
valid_config.webgit.git_user      = 'gitlab'
valid_config.webgit.remotes_bin   = '/githome/git/bin/remotes'
valid_config.webgit.identity_file = '~getup/.ssh/id_rsa'
valid_config.webgit.pubkey_file   = '~getup/getup-rest-api/.ssh/authorized_keys'

valid_config.provider.openshift.hostname         = 'broker.ops.getupcloud.com'
valid_config.provider.openshift.gear_profile     = 'production'
valid_config.provider.openshift.dev_gear_profile = 'development'

def validate(node, valid):
	for k, v in node.iteritems():
		if isinstance(v, dict):
			if k not in valid:
				raise NameError(k)
			validate(v, valid[k])
		elif isinstance(v, basestring):
			node[k] = os.path.expanduser(os.path.expandvars(v))

def loadconfig(app, filename=None):
	_file = os.environ.get('CONFIG_FILE', filename or app_root/'getup-rest-api.conf')
	_g, _l = {}, Tree(**valid_config)
	print '## Loading config file: %s' % _file
	try:
		with open(_file) as f:
			exec(f, _g, _l)
	except NameError, ex:
		raise NameError('Invalid config (%s): %s' % (_file, ex))

	try:
		validate(_l, valid_config)
		_l.database.url = _l.database.url.format(**_l.database.config)
	except NameError, ex:
		raise Exception('Invalid config "%s" while loading "%s"' % (ex, _file))

	if isinstance(app, dict):
		app.update(_l)
		return app
	else:
		app.config.update(_l)
		return app.config

if __name__ == '__main__':
	import sys, json
	try:
		print json.dumps(loadconfig({}, sys.argv[1]), indent=3)
	except Exception, ex:
		print '##', ex
		sys.exit(1)
