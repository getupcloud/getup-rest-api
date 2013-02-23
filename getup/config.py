# -*- coding: utf-8 -*-

from path import path as Path
import os

app_root = Path(os.environ.get('APP_ROOT', Path(__file__).dirname().dirname()))

valid_config = [
	'database',
	'webgit',
	'provider',
]

def loadconfig(app, filename=None):
	_file = os.environ.get('CONFIG_FILE', filename or app_root/'getup-rest-api.conf')
	_ns = dict()
	print '## Loading config file: %s' % _file
	with open(_file) as f:
		exec f.read() in _ns

	_conf = {}
	# read only valid sections
	for section, value in filter(lambda (a, b): a in valid_config, _ns.iteritems()):
		_conf[section] = { k: os.path.expanduser(os.path.expandvars(v)) if isinstance(v, basestring) else v for k, v in value.iteritems() }

	if isinstance(app, dict):
		app.update(_conf)
		return app
	else:
		app.config.update(_conf)
		return app.config
