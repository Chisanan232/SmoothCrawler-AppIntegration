from smoothcrawler.factory import _chk_factory_type, CrawlerFactory as _CrawlerFactory
from typing import Generic

from .role.framework import ApplicationIntegrationRole
from .types import BaseRole



class ApplicationIntegrationFactory(_CrawlerFactory):

    _ApplicationIntegrationRole: BaseRole = None

    @property
    def app_integration_role(self) -> Generic[BaseRole]:
        return self._ApplicationIntegrationRole


    @app_integration_role.setter
    def app_integration_role(self, role: Generic[BaseRole]) -> None:
        _chk_factory_type(role, ApplicationIntegrationRole)
        self._ApplicationIntegrationRole = role

