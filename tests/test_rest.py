from webtest import TestApp
from getup import rest
import prepare_db

users = prepare_db.users

def setup_module(module):
	setattr(module, 'app', TestApp(rest.app))
	prepare_db.init_database()

def teardown_module():
	prepare_db.drop_database()

def _test_url(path, **methods):
	'''Makes a request on 'path' for each 'method=status' from 'methods'.
	'''
	params = methods.pop('params', None)
	for method, status in methods.iteritems():
		call_method = getattr(app, method)
		if method in [ 'post', 'put' ]:
			call_method(path, status=status, params=params or '')
		else:
			call_method(path, status=status)

def test_rest_root():
	_test_url('/status', post=405, put=405, delete=405)
	app.head('/').status_code == 200
	app.get('/').status_code == 200

def test_rest_status():
	_test_url('/status', post=405, put=405, delete=405, get=403)
	_test_url('/status', post=405, put=405, delete=405, get=403, params={'private_token': users['blocked']['authentication_token']})
	_test_url('/status', post=405, put=405, delete=405, get=403, params={'private_token': users['unknown']['authentication_token']})
	_test_url('/status', post=405, put=405, delete=405, get=403, params={'private_token': users['valid']['authentication_token']})
	app.get('/status', params={'private_token': users['admin']['authentication_token']})

def test_rest_broker_domains():
	_test_url('/broker/rest/domains', post=401, put=401, delete=401, get=401)
	#_test_url('/broker/rest/domains', post=401, put=401, delete=401, get=401, params={'private_token': users['unknown']['authentication_token']})
	#print app.get('/broker/rest/domains')
	#_test_url('/broker/rest/domains', get=200, params={'private_token': users['valid']['authentication_token']})
