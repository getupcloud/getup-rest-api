# -*- coding: utf-8 -*-

class Status(dict):
	def __init__(self, config, **kvargs):
		self['config'] = self._mask_config(config)
		self.update(kvargs)

	def _mask_config(self, config):
		cfg = {}
		mask = [ 'pass', 'passwd', 'password', 'token', 'key', 'secret' ]
		exclude = [ 'engine' ]
		for k, v in config.iteritems():
			if k in exclude:
				continue
			elif isinstance(v, dict):
				cfg[k] = self._mask_config(v)
			else:
				cfg[k] = '***' if k in mask else v
		return cfg

from index import *
import user
import status
