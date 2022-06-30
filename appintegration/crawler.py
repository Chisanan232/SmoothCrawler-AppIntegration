from smoothcrawler.components.persistence import PersistenceFacade as _PersistenceFacade
from smoothcrawler.components.httpio import BaseHTTP as _BaseHttpIo
from smoothcrawler.components.data import (
    BaseHTTPResponseParser as _BaseHTTPResponseParser,
    BaseDataHandler as _BaseDataHandler,
    BaseAsyncDataHandler as _BaseAsyncDataHandler
)
from smoothcrawler.crawler import BaseCrawler
from typing import List, Dict, Iterable, Any, Union, Optional, Generic, cast
from abc import ABC, abstractmethod

from .task.messagequeue import MessageQueueConfig as _MessageQueueConfig
from .factory import ApplicationIntegrationFactory as _ApplicationIntegrationFactory
from .types import BaseRole as _BaseRole



class BaseApplicationIntegrationCrawler(BaseCrawler):

    def __init__(self, factory: _ApplicationIntegrationFactory = None):
        super(BaseApplicationIntegrationCrawler, self).__init__(factory=factory)
        self._factory = cast(_ApplicationIntegrationFactory, self._factory)


    def _initial_factory(self) -> _ApplicationIntegrationFactory:
        return _ApplicationIntegrationFactory()


    @property
    def factory(self) -> _ApplicationIntegrationFactory:
        return self._factory


    def register_factory(self,
                         http_req_sender: _BaseHttpIo = None,
                         http_resp_parser: _BaseHTTPResponseParser = None,
                         data_process: Union[_BaseDataHandler, _BaseAsyncDataHandler] = None,
                         persistence: _PersistenceFacade = None,
                         app_processor_role: Generic[_BaseRole] = None,
                         app_source_role: Generic[_BaseRole] = None,
                         data_process_before_back: Generic[_BaseRole] = None) -> None:
        super(BaseApplicationIntegrationCrawler, self).register_factory(
            http_req_sender=http_req_sender,
            http_resp_parser=http_resp_parser,
            data_process=data_process,
            persistence=persistence
        )
        self._factory.app_processor_role = app_processor_role
        self._factory.app_source_role = app_source_role
        self._factory.data_handling_before_back = data_process_before_back


    @abstractmethod
    def get_target(self, **kwargs) -> dict:
        pass


    @abstractmethod
    def run(self, **kwargs) -> Optional[Any]:
        pass


    @abstractmethod
    def run_and_save(self, **kwargs) -> Optional[Any]:
        pass


    @abstractmethod
    def run_and_back_to_middle(self, **kwargs) -> Optional[Any]:
        pass


    def data_parameters(self, data: Dict) -> Dict[str, Any]:
        _url = data.get("url", None)
        _method = data.get("method", None)

        _kwargs = {
            "method": _method,
            "url": _url
        }
        return _kwargs


    @abstractmethod
    def send_to_app_integration_middle_component(self, data: Iterable) -> None:
        pass



class AppIntegrationCrawler(BaseApplicationIntegrationCrawler, ABC):

    def run(self, **kwargs) -> Optional[Any]:
        _target = kwargs.get("target")
        _kwargs = self.data_parameters(data=_target)
        _parsed_response = self.crawl(**_kwargs)
        _data = self.data_process(parsed_response=_parsed_response)
        return _data


    def run_and_save(self, **kwargs) -> None:
        _target = kwargs.get("target")
        _data = self.run(target=_target)
        self.persist(data=_data)


    def run_and_back_to_middle(self, **kwargs) -> None:
        """
        Run the crawling task and write or send, etc back to the middle component like file,
        shared database, connection like TCP, message queue system.

        :return:
        """

        _target = kwargs.get("target")
        _data = self.run(target=_target)
        self.send_to_app_integration_middle_component(data=_data)



class FileBasedCrawler(AppIntegrationCrawler):

    def get_target(self, **kwargs) -> Dict:
        # # Working procedure
        # 1. Keep listening the targets (it maybe files, database, connection like TCP, message queue middle system).
        # 2. If it get anything it would run the task with the data.
        # # By the way, it should has some different scenarios like just check once or keep checking it
        # # again and again until timeout time or others you set.
        _data = self._factory.app_processor_role.run_process()
        return _data


    def data_parameters(self, data: list) -> Dict[str, Any]:
        _url = data[0]
        _method = data[1]
        _kwargs = {
            "method": _method,
            "url": _url
        }
        return _kwargs


    def send_to_app_integration_middle_component(self, data: Iterable) -> None:
        _data = self._factory.data_handling_before_back.process(data=data)
        self._factory.app_source_role.run_process(data=_data)



class MessageQueueCrawler(AppIntegrationCrawler):

    def get_target(self, config: _MessageQueueConfig, poll_args: dict) -> None:
        # # Working procedure
        # 1. Keep listening the targets (it maybe files, database, connection like TCP, message queue middle system).
        # 2. If it get anything it would run the task with the data.
        # # By the way, it should has some different scenarios like just check once or keep checking it
        # # again and again until timeout time or others you set.
        self._factory.app_processor_role.run_process(config=config, poll_args=poll_args)


    def run(self, targets: dict, config: _MessageQueueConfig, poll_args: dict) -> None:
        poll_args["callback"] = super(MessageQueueCrawler, self).run
        self.get_target(config=config, poll_args=poll_args)


    def run_and_save(self, targets: dict, config: _MessageQueueConfig, poll_args: dict) -> None:
        poll_args["callback"] = super(MessageQueueCrawler, self).run_and_save
        self.get_target(config=config, poll_args=poll_args)


    def run_and_back_to_middle(self, targets: dict, config: _MessageQueueConfig, poll_args: dict) -> None:
        poll_args["callback"] = super(MessageQueueCrawler, self).run_and_back_to_middle
        self.get_target(config=config, poll_args=poll_args)


    def send_to_app_integration_middle_component(self, data: Iterable) -> None:
        print(f"[DEBUG] get data: {data} and it would send it back to application integration system.")
        pass

