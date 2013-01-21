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
	repo = api.get_project(name)

	cmd = "cd /home/git/repositories/%s.git && { git remote add app '%s' || git remote set-url app '%s'; }"  % (project, gear, gear)
	ret = ssh.run(cmd)
	print '>' * 30
	print ret
	print '<' * 30
	if ret.returncode != 0:
		return 'ERROR: %s' % ret.stderr
	else:
		return 'OK'
