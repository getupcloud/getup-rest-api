import os
import bottle
import getup

app = bottle.app()

# fill test database
engine = app.config.database['engine']
test_user = os.environ.get('TESTUSER', 'user@test.com:pass:token')
test_user = dict(zip(['email', 'encrypted_password', 'authentication_token'], test_user.split(':')))
getup.database.Users.insert().values(name='testuser', admin=False, blocked=False, username='Test User', **test_user).execute()
query = getup.database.Users.select()

print '## Test User:'
for u in query.execute():
	print '### %s' % u

print '## Starting application server.'
bottle.run(server='gunicorn', host='127.0.0.1', port='8080', debug=True, reloader=True)
print '## Finished application server.'
