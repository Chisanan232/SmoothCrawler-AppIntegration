from smoothcrawler.factory import _chk_factory_type, CrawlerFactory as _CrawlerFactory
from typing import TypeVar, Generic

from .role.framework import ApplicationIntegrationRole as _ApplicationIntegrationRole
from .components import DataHandlerBeforeBack as _DataHandlerBeforeBackObj


_BaseRole = TypeVar("_BaseRole", bound=_ApplicationIntegrationRole)
_DataHandlerBeforeBack = TypeVar("_DataHandlerBeforeBack", bound=_DataHandlerBeforeBackObj)


class ApplicationIntegrationFactory(_CrawlerFactory):

    _AppIntegrationSourceRole: _BaseRole = None
    _DataHandlerBeforeBackFactory: _DataHandlerBeforeBack = None
    _AppIntegrationProcessorRole: _BaseRole = None

    @property
    def app_source_role(self) -> Generic[_BaseRole]:
        return self._AppIntegrationSourceRole


    @app_source_role.setter
    def app_source_role(self, role: Generic[_BaseRole]) -> None:
        _chk_factory_type(role, _ApplicationIntegrationRole)
        self._AppIntegrationSourceRole = role


    @property
    def data_handling_before_back(self) -> Generic[_DataHandlerBeforeBack]:
        return self._DataHandlerBeforeBackFactory


    @data_handling_before_back.setter
    def data_handling_before_back(self, role: Generic[_DataHandlerBeforeBack]) -> None:
        _chk_factory_type(role, _DataHandlerBeforeBackObj)
        self._DataHandlerBeforeBackFactory = role


    @property
    def app_processor_role(self) -> Generic[_BaseRole]:
        return self._AppIntegrationProcessorRole


    @app_processor_role.setter
    def app_processor_role(self, role: Generic[_BaseRole]) -> None:
        _chk_factory_type(role, _ApplicationIntegrationRole)
        self._AppIntegrationProcessorRole = role

