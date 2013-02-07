# -*- coding: utf-8 -*-

import bottle
from getup import aaa, provider, codec, gitlab, http
from getup.response import response

@aaa.authoritative_user
@provider.provider
@gitlab.api
@gitlab.ssh
def post(domain, name, user, prov, api, ssh):
	try:
		project = bottle.request.params['name']
	except KeyError:
		return response(user, status=http.HTTP_UNPROCESSABLE_ENTITY)

	# retrieve openshift app
	res = prov.get_app(domain=domain, name=name)
	if not res.ok:
		return response(user, res)
	app = res.json['data']

	# retrieve gitlab project
	res = api.get_project(project)
	if not res.ok:
		return response(user, res)
	proj = res.json

	# add git remote 'app' to project repository
	# pointing to openshift gear repository.
	values = dict(
		git_host=app.config.webgit['hostname'],
		project=project.replace('/', '').replace('.', ''),
		**app)
	values['remote'] = '%(project)s@%(name)s-%(domain_id)s' % values
	# TODO: parametrize paths and remote name
	cmd = '''
	set -xe
	TMP_REPO="`mktemp -d`"
	cd "$TMP_REPO"
	{
		git clone '%(git_url)s' '%(project)s' &&
		cd '%(project)s' &&
		git push 'git@%(git_host)s:%(project)s.git' master
	} && STATUS=$? || STATUS=$?
	rm -rf "$TMP_REPO"
	[ "$STATUS" -eq 0 ] || exit $STATUS
	cd ~git/repositories/%(project)s.git
	git remote add '%(remote)s' '%(git_url)s' || git remote set-url '%(remote)s' '%(git_url)s'
	git fetch '%(remote)s' master
	''' % values

	ret = ssh.run(cmd)

	if ret.returncode != 0:
		return 'ERROR: %s' % ret.stderr
	else:
		return 'OK'
