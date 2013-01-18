# -*- coding: utf-8 -*-

import json
import database
import bottle

def accounting(**labels):
	'''Possible labels:
		HTTP_METHOD:'event_name'
		HTTP_METHOD:('event_name', validation_callback)
	'''
	class Accounter:
		def __init__(self, wrapped):
			if not labels:
				raise ValueError('Missing accounting labels')
			self.wrapped = wrapped
			self.labels = labels
			if 3 < len(labels) < 1:
				raise TypeError('Invalid accounting label: %r' % l)
			for l in labels.values():
				if not isinstance(l, (basestring, list, tuple, dict)):
					raise TypeError('Invalid accounting label: %r' % l)
		def __call__(self, *vargs, **kvargs):
			res = self.wrapped(*vargs, **kvargs)

			label = self.labels.get(bottle.request.method, None)
			if label is None:
				return res

			filter_callback, filter_data_callback = None, None
			if len(label) == 3:
				event_name, filter_callback, filter_data_callback = label
			elif len(label) == 2:
				event_name, filter_callback = label
			else:
				event_name = label

			if callable(filter_callback):
				if not filter_callback(res):
					return res

			if callable(filter_data_callback):
				save_data = filter_data_callback(bottle.request.body.read(-1))
			else:
				save_data = bottle.request.body.read(-1)

			if 200 <= res.status_code < 300:
				event_value = {
					'req_url': res.request.path_url,
					'req_data': save_data,
					'res_status': res.status_code,
				}
				account(user=res.user, event_name=event_name, event_value=event_value)
			return res
	return Accounter

def account(user, event_name, event_value):
	if not isinstance(event_value, basestring):
		event_value=json.dumps(event_value)
	database.accounting(user=user, event_name=event_name, event_value=event_value)
	print 'ACCOUNT:', user.email, event_name
