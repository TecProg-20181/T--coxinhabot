class Help(object):

	HELP = """
	 /new NOME
	 /todo ID
	 /doing ID
	 /done ID
	 /delete ID
	 /list
	 /rename ID NOME
	 /dependson ID ID...
	 /duplicate ID
	 /showPriority
	 /priority ID PRIORITY{low, medium, high}
	 /help
	"""
	
	def get_help(self):
		
		return self.HELP