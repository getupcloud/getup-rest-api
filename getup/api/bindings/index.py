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

	# retrieve openshift app
	res = prov.get_app(domain=domain, name=name)
	if not res.ok:
		return response(user, res)
	app = res.json['data']

	# retrieve gitlab project
	res = api.get_project(name)
	if not res.ok:
		return response(user, res)
	proj = res.json

	# add git remote 'app' to project repository
	# poiting to openshift gear repository.
	values = dict(project=project.replace('/', ''), **data)
	# TODO: parametrize paths and remote name
	cmd = '''
	cd /home/git/repositories/%(project)s.git
	git remote add app '%(git_url)s' || git remote set-url app '%(git_url)s'
	'''  % values

	ret = ssh.run(cmd)

	if ret.returncode != 0:
		return 'ERROR: %s' % ret.stderr
	else:
		return 'OK'
