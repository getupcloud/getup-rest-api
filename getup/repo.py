import git

class Repo:
	class Progress(git.remote.RemoteProgress):
		NAMES = {
			git.remote.RemoteProgress.COUNTING: 'counting',
			git.remote.RemoteProgress.COMPRESSING: 'compressing',
			git.remote.RemoteProgress.WRITING: 'writing',
			git.remote.RemoteProgress.RECEIVING: 'receiving',
			git.remote.RemoteProgress.RESOLVING: 'resolving',
		}

		def update(self, op_code, cur_count, max_count, message):
			if (op_code & self.STAGE_MASK) == self.BEGIN:
				print 'git:  ', self.NAMES[op_code & self.OP_MASK]
				#sys.stdout.flush()
			#print '>> %s %s/%s %s' % (op_code, cur_count, max_count, message)

	def __init__(self, app):
		name = app['name']
		try:
			self.git = git.Repo(name)
			print '! repo(%(name)s)' % app
		except git.NoSuchPathError:
			url = app['git_url']
			print 'git: cloning'
			self.git = git.Repo.clone_from(url, name, Repo.Progress())
			print '\n+ repo(%(name)s, %(git_url)s)' % app
		self.path = self.git.working_dir

