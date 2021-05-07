import inspect
from colorama import Fore
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Tuple, Union

from .plugin import HandlerType

class ProviderRunner:
	def __init__(self, providers: Dict, event_registry: Dict):
		self._providers: Dict = providers
		self._event_registry: Dict = event_registry

	def download(self, provider_id: str, metadata: Dict) -> Tuple[Path, str]:
		try:
			provider = self._providers[provider_id]
		except KeyError:
			return (Path.cwd(), f"[ERROR] Could not locate mod provider with id '{provider_id}'")

		try:
			handler = provider["download"]
		except KeyError:
			return (Path.cwd(), f"[ERROR] Mod provider '{provider_id}' does not provide a download handler.")

		# Since the handler is supposed to be a method, we need to provide the class instance as the self parameter.
		return handler(provider["instance"], metadata)

	def generate(self, provider_id: str) -> Tuple[Dict, str]:
		try:
			provider = self._providers[provider_id]
		except KeyError:
			return ({}, f"[ERROR] Could not locate mod provider with id '{provider_id}'")

		try:
			handler = provider["generate"]
		except KeyError:
			return ({}, f"[ERROR] Mod provider '{provider_id}' does not provide a generation handler.")

		# Since the handler is supposed to be a method, we need to provide the class instance as the self parameter.
		return handler(provider["instance"])

	def __str__(self) -> str:
		return f"Providers: {self._providers}; Event Registry: {self._event_registry};"

def load_providers(providers: List[Union[str, ModuleType]]) -> ProviderRunner:
	"""Loads providers to be used by the MCMM plugin engine
	
	Arguments:
		providers {List[str]} -- List of providers to load
	"""
	
	return_providers = {} # {"provider id": {"instance": provider_class, "misc metadata (listeners, configs, requirements, etc.)": "the data"}}
	return_event_registry = {}

	# Initialize event registry with empty lists to prevent KeyErrors elsewhere
	for h_type in HandlerType._all_types:
		return_event_registry[h_type] = []

	for provider in providers:
		# Import the provider's module if the parameter is not already a module
		if inspect.ismodule(provider):
			provider_module = provider
		else:
			provider_module = import_module(provider)
		
		# Find all classes in the provider's module
		all_module_classes = [m[1] for m in inspect.getmembers(provider_module, inspect.isclass) if m[1].__module__ == provider_module.__name__]
		
		# Find all classes marked with the Class._is_mcmm_plugin variable set to True
		mcmm_provider_classes = []
		for module_class in all_module_classes:
			try:
				if not module_class._is_mcmm_plugin:
					continue
			except AttributeError:
				continue
			
			mcmm_provider_classes.append(module_class)

		# Recommended amount of @MCMMPlugin decorators sanity check
		if len(mcmm_provider_classes) == 0:
			print(f"{Fore.YELLOW}[WARNING] Could not find an MCMM provider class in {provider}. Maybe it is missing the @MCMMPlugin decoration?{Fore.RESET}")
		elif len(mcmm_provider_classes) > 1:
			print(f"{Fore.YELLOW}[WARNING] {provider} provided more than one MCMM plugin class. The recommended limit is one per module.{Fore.RESET}")

		# Identify functions that have
		for provider_class in mcmm_provider_classes:
			provider_instance = provider_class()
			provider_id = provider_instance.id

			# Store an instance of the provider
			return_providers[provider_id] = {"instance": provider_instance}

			# Discovers and adds the handlers
			for _, func in inspect.getmembers(provider_class, inspect.isfunction):
				try:
					if not func._is_mcmm_handler:
						continue
				except AttributeError as e:
					continue

				# Sort into different types
				try:
					# Check if valid event type
					if func._mcmm_event not in HandlerType._all_types:
						print(f"{Fore.RED}[ERROR] Function '{func.__name__}' of '{provider_id}' has invalid event type '{func._mcmm_event}'{Fore.RESET}'")

					return_providers[provider_id][func._mcmm_event] = func
					
					if func._mcmm_event not in return_event_registry:
						return_event_registry[func._mcmm_event] = []

					return_event_registry[func._mcmm_event].append(provider_id)

				except AttributeError:
					print(f"{Fore.RED}[ERROR] '{func.__name__}' of '{provider_id}' was marked as an MCMM event handler but did not specify the event to handle!{Fore.RESET}")

	return ProviderRunner(return_providers, return_event_registry)
