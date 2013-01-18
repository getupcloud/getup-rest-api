# -*- coding: utf-8 -*-

import bottle
import json
from getup import aaa, codec, provider, http
from getup import database, gitlab, util, hooks
from getup.response import response

def post():
	# POST/DELETE key to/from openshift.
	# If it was triggered by gitlab's system hooks (web or /api), broker will return OK.
	# If it was triggered by api (/broker), broker will return 409-120/121 since /broker
	# already posted the key (not a big concern right now).
	user = None
	event = bottle.request.json
	print 'HOOK EVENT:', event
	if event['event_name'] in [ 'key_save', 'key_destroy' ]:
		user = database.user(email=event['owner_email'])
		prov = provider.OpenShift(username=user['email'], password=user['authentication_token'])

		if event['event_name'] == 'key_save':
			try:
				type, key , _ = event['key'].split()
			except:
				type, key = event['key'].split()
			res = prov.add_key(name=event['title'], type=type, content=key)
		else:
			res = prov.del_key(name=event['title'])
	elif event['event_name'] in [ 'project_create', 'project_destroy' ]:
		user = database.user(email=event['owner_email'])
		ev_name = 'create_proj' if event['event_name'] == 'project_create' else 'delete_proj'
		ev_value = {
			'req_url': event['name'],
			'req_data': json.dumps(event),
			'res_status': 200,
		}
		hooks.account(user, ev_name, ev_value)
	else:
		return response(user=None, status=http.HTTP_OK)
	return response(user, res)
