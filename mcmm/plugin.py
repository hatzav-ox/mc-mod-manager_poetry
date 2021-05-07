from abc import ABC, abstractmethod

class PluginBase(ABC):
	@property
	@abstractmethod
	def id(self):
		pass

	@property
	@abstractmethod
	def help_string(self):
		pass

def MCMMPlugin(plugin_class):
	plugin_class._is_mcmm_plugin = True
	return plugin_class

def DownloadHandler(func):
	func._is_mcmm_handler = True
	func._mcmm_event = HandlerType.download
	return func

def GenerationHandler(func):
	func._is_mcmm_handler = True
	func._mcmm_event = HandlerType.generate
	return func

class HandlerType:
	download = "download"
	generate = "generate"

	_all_types = ["download", "generate"]
