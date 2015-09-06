class Node(object):
	def __init__(self, nodeType, value=None):
		self.type = nodeType
		self.value = value
		self.children = []

	@classmethod
	def fromToken(cls, token):
		return cls(token.type, token.value)