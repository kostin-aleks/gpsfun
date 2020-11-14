class InfoHolder(object):

    def __init__(self):
        self._registry = []

    def register_plugin(self, func):
        self._registry.append(func)
