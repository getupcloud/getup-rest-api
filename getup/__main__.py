import bottle
import getup

app = bottle.app()

# fill test database
engine = app.config.database['engine']
getup.database.Users.insert().values(email='user@test.com', encrypted_password='pass', name='usertest', admin=False, authentication_token='token', blocked=False, username='User Test').execute()
query = getup.database.Users.select()

print '## Users:'
for u in query.execute():
	print '### %s' % u

print '## Starting application server.'
bottle.run(host='localhost', port=8080, debug=True, reloader=True)
print '## Finished application server.'
