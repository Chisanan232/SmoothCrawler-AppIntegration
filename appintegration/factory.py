from smoothcrawler.factory import _chk_factory_type, CrawlerFactory as _CrawlerFactory
from typing import TypeVar, Generic

from .role.framework import ApplicationIntegrationRole
from .components import DataHandlerBeforeBack
from .types import BaseRole


_DataHandlerBeforeBack = TypeVar("_DataHandlerBeforeBack", bound=DataHandlerBeforeBack)


class ApplicationIntegrationFactory(_CrawlerFactory):

    _AppIntegrationSourceRole: BaseRole = None
    _DataHandlerBeforeBackFactory: _DataHandlerBeforeBack = None
    _AppIntegrationProcessorRole: BaseRole = None

    @property
    def app_source_role(self) -> Generic[BaseRole]:
        return self._AppIntegrationSourceRole


    @app_source_role.setter
    def app_source_role(self, role: Generic[BaseRole]) -> None:
        _chk_factory_type(role, ApplicationIntegrationRole)
        self._AppIntegrationSourceRole = role


    @property
    def data_handling_before_back(self) -> Generic[_DataHandlerBeforeBack]:
        return self._DataHandlerBeforeBackFactory


    @data_handling_before_back.setter
    def data_handling_before_back(self, role: Generic[_DataHandlerBeforeBack]) -> None:
        _chk_factory_type(role, DataHandlerBeforeBack)
        self._DataHandlerBeforeBackFactory = role


    @property
    def app_processor_role(self) -> Generic[BaseRole]:
        return self._AppIntegrationProcessorRole


    @app_processor_role.setter
    def app_processor_role(self, role: Generic[BaseRole]) -> None:
        _chk_factory_type(role, ApplicationIntegrationRole)
        self._AppIntegrationProcessorRole = role

