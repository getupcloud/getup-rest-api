# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider, codec, gitlab
from getup.response import response

@aaa.authoritative_user
@provider.provider
@gitlab.api
@gitlab.ssh
def post(user, prov, api, ssh):
	try:
		params = bottle.request.params
		domain, name, project = params['domain'], params['name'], params['project']
	except KeyError:
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)
	res = prov.get_app(domain=params['domain'], name=params['name'])
	data = res.json['data']
	gear = data['git_url']
	stdin, stdout, stderr = ssh.exec_command('cd /tmp')
	print [ '> %s' % l for l in stdout.readlines() ]
	stdin, stdout, stderr = ssh.exec_command('ls -la')
	print [ '> %s' % l for l in stdout.readlines() ]
	return gear
