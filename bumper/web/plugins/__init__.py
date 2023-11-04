"""Webserver plugin module."""
import inspect
import logging
import os
import sys
from abc import abstractmethod
from collections.abc import Iterable
from glob import glob
from os.path import isfile
from types import ModuleType

from aiohttp import web
from aiohttp.web_routedef import AbstractRouteDef


class WebserverPlugin:
    """Abstract webserver plugin."""

    @property
    @abstractmethod
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        raise NotImplementedError


def _add_routes(app: web.Application, module: ModuleType, plugin_module_name: str) -> None:
    if not module.__name__.startswith(plugin_module_name):
        return

    assert module.__file__ is not None
    if module.__file__.endswith("__init__.py"):
        sub_app = web.Application()
    else:
        sub_app = app

    for _, clazz in inspect.getmembers(module, inspect.isclass):
        if issubclass(clazz, WebserverPlugin) and clazz != WebserverPlugin:
            web_obj: WebserverPlugin = clazz()
            sub_app.add_routes(web_obj.routes)
            logging.debug(f"Added routes from {clazz.__name__}")

    for _, obj in inspect.getmembers(module, inspect.ismodule):
        _add_routes(sub_app, obj, plugin_module_name)

    if module.__file__.endswith("__init__.py"):
        prefix = os.path.dirname(module.__file__)
        prefix = prefix[prefix.rfind(os.path.sep) :] + os.path.sep
        app.add_subapp(prefix, sub_app)


def _import_plugins(module: ModuleType) -> None:
    assert module.__file__ is not None

    plugin_files = [
        file
        for file in glob(os.path.join(os.path.dirname(module.__file__), "**/*.py"), recursive=True)
        if isfile(file) and file != module.__file__
    ]

    for file in plugin_files:
        plugin_name = None
        try:
            plugin_name = file.replace(os.path.sep, ".")
            plugin_name = plugin_name[plugin_name.find(module.__name__) : -3].removesuffix(".__init__")
            imported_module = __import__(plugin_name, fromlist=["*"])
            logging.debug(f"Imported plugin module: {imported_module.__name__}")
        except Exception as e:
            logging.error(f"Failed to import plugin module {plugin_name}: {e}")


def add_plugins(app: web.Application) -> None:
    """Discover and add all plugins to app."""
    module = sys.modules[__name__]
    _import_plugins(module)

    plugin_module_name = module.__name__
    for _, obj in inspect.getmembers(module, inspect.ismodule):
        if obj.__name__.startswith(plugin_module_name):
            _add_routes(app, obj, plugin_module_name)
