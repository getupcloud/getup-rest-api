from getup import database

users = {
	'unknown': {
		'authentication_token': 'unknown-token',
	},
	'admin': {
		'email': 'admin@foo.bar',
		'name': 'Admin',
		'username': 'admin',
		'encrypted_password': 'admin-enc-password',
		'authentication_token': 'admin-token',
		'blocked': False,
		'admin': True,
	},
	'blocked': {
		'email': 'blocked@foo.bar',
		'name': 'Blocked User',
		'username': 'blocked',
		'encrypted_password': 'blocked-enc-password',
		'authentication_token': 'blocked-token',
		'blocked': True,
		'admin': False,
	},
	'valid': {
		'email': 'valid@foo.bar',
		'name': 'Valid User',
		'username': 'valid',
		'encrypted_password': 'valid-enc-password',
		'authentication_token': 'valid-token',
		'blocked': False,
		'admin': False,
	},
}

def init_database():
	for i, (name, data) in enumerate(users.iteritems()):
		if name != 'unknown':
			database.Users.insert().values(id=i, **data).execute()

def drop_database():
	database.Users.delete()
