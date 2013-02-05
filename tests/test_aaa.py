import bottle
import base64
from webtest import TestApp
from getup import aaa
import prepare_db

users = prepare_db.users

def setup_module(module):
	setattr(module, 'app', TestApp(aaa.app))
	prepare_db.init_database()

def teardown_module():
	prepare_db.drop_database()

@bottle.route('/internal-test/auth/valid')
@aaa.valid_user
def internal_test_auth():
	return 'ok'

def test_auth_user():
	valid_email = users['valid']['email']
	valid_token = users['valid']['authentication_token']
	valid_basic_token = base64.encodestring('%s:%s' % (valid_email, valid_token))
	valid_basic_token_header = 'Basic %s' % valid_basic_token
	blocked_token = users['blocked']['authentication_token']

	# test extracting credentials
	assert aaa._get_auth_token({'private_token': valid_token}, None) == ('', valid_token)
	assert aaa._get_auth_token({'token': valid_token}, None)         == ('', valid_token)
	assert aaa._get_auth_basic(None, {'Authorization': valid_basic_token_header}) == (valid_email, valid_token)

	# assert valid users can authenticate
	app.get('/internal-test/auth/valid', params={'private_token': valid_token})
	app.get('/internal-test/auth/valid', params={'token': valid_token})
	app.get('/internal-test/auth/valid', headers={'Authorization': valid_basic_token_header.lower()})
	# assert blocked users cant authenticate
