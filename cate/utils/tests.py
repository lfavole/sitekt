class DefaultArgs:
	"""
	Dict that can be edited when called.
	Example :
	>>> DefaultArgs({"a": "b", "c": "d", "e": "f"})(a = REMOVED, c = "e")
	{"c": "e", "e": "f"}
	"""
	REMOVED = object()

	def __init__(self, args_dict: dict):
		self.dict = args_dict

	def __call__(self, **names):
		args = self.dict.copy()
		for name, value in names.items():
			if value == self.REMOVED:
				args.pop(name)
			else:
				args[name] = value
		return args

REMOVED = DefaultArgs.REMOVED
