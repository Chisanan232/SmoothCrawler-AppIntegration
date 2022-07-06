from smoothcrawler.components.persistence import PersistenceFacade as _PersistenceFacade
from smoothcrawler.components.httpio import BaseHTTP as _BaseHttpIo
from smoothcrawler.components.data import (
    BaseHTTPResponseParser as _BaseHTTPResponseParser,
    BaseDataHandler as _BaseDataHandler,
    BaseAsyncDataHandler as _BaseAsyncDataHandler
)
from smoothcrawler.crawler import BaseCrawler
from typing import List, Dict, Iterable, Callable, Generator, Any, TypeVar, Union, Optional, Generic, cast
from abc import ABC, abstractmethod
import json
import time

from .task.messagequeue import MessageQueueConfig as _MessageQueueConfig
from .role.framework import (
    ApplicationIntegrationRole as _ApplicationIntegrationRole,
    BaseProducer as _BaseProducer,
    BaseConsumer as _BaseConsumer
)
from .factory import ApplicationIntegrationFactory as _ApplicationIntegrationFactory


_BaseRole = TypeVar("_BaseRole", bound=_ApplicationIntegrationRole)


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
    def _run_process_with_target(self, **kwargs) -> None:
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
    def send_to_app_integration_middle_component(self, **kwargs) -> None:
        pass



class AppIntegrationCrawler(BaseApplicationIntegrationCrawler, ABC):

    def run(self, **kwargs) -> List[Any]:

        def _run_process(_target: dict) -> Optional[Any]:
            _kwargs = self.data_parameters(data=_target)
            _parsed_response = self.crawl(**_kwargs)
            _data = self.data_process(parsed_response=_parsed_response)
            return _data

        _target = kwargs.get("target")
        _run_result = None

        if type(_target) is dict:
            _run_result = [_run_process(_target=_target)]
        elif type(_target) is list:
            _run_result = [_run_process(_target=_target_row) for _target_row in _target]
        elif type(_target) is str:
            _json_target = json.loads(_target)
            _run_result = [_run_process(_target=_json_target)]
        elif type(_target) is bytes:
            _decoded_target = _target.decode("utf-8")
            _json_target = json.loads(_decoded_target)
            _run_result = [_run_process(_target=_json_target)]
        else:
            raise TypeError("Option *target* only accept dict or list type data.")

        return _run_result


    @abstractmethod
    def run_and_save(self, **kwargs) -> None:
        _target = kwargs.get("target")
        _data = self.run(target=_target)
        self.persist(data=_data)


    @abstractmethod
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

    def _run_process_with_target(self, callback: Callable, scrape_time: int = 10, limit_time: int = -1, limit_get_target_time: int = -1) -> Generator:
        # # Working procedure
        # 1. Keep listening the targets (it maybe files, database, connection like TCP, message queue middle system).
        # 2. If it get anything it would run the task with the data.
        # # By the way, it should has some different scenarios like just check once or keep checking it
        # # again and again until timeout time or others you set.

        if limit_time < 0 and limit_time != -1:
            raise ValueError
        if limit_get_target_time < 0 and limit_get_target_time != -1:
            raise ValueError

        _current_time = 0
        _get_target_time = 0

        while True:
            _current_time += 1

            try:
                _data = self._factory.app_processor_role.run_process()
            except FileNotFoundError:
                pass
            else:
                _get_target_time += 1
                yield callback(target=_data)

            # If both of options *limit_time* and *limit_get_target_time* have been set, it would use option *limit_get_target_time*.
            if limit_get_target_time != -1:
                if 0 <= limit_get_target_time <= _get_target_time:
                    break
            else:
                if 0 <= limit_time <= _current_time:
                    break

            time.sleep(scrape_time)


    def run(self, scrape_time: int = 10, limit_time: int = -1, limit_get_target_time: int = -1) -> Generator:
        return self._run_process_with_target(
            callback=super(FileBasedCrawler, self).run,
            scrape_time=scrape_time,
            limit_time=limit_time,
            limit_get_target_time=limit_get_target_time
        )


    def run_and_save(self, scrape_time: int = 10, limit_time: int = -1, limit_get_target_time: int = -1) -> None:
        _running_results = self.run(scrape_time=scrape_time, limit_time=limit_time, limit_get_target_time=limit_get_target_time)
        for _results in _running_results:
            for _result_row in _results:
                self.persist(data=_result_row)


    def run_and_back_to_middle(self, scrape_time: int = 10, limit_time: int = -1, limit_get_target_time: int = -1) -> None:
        _running_results = self.run(scrape_time=scrape_time, limit_time=limit_time, limit_get_target_time=limit_get_target_time)
        for _results in _running_results:
            for _result_row in _results:
                self.send_to_app_integration_middle_component(data=_result_row)


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

    _Running_Result: list = []

    def _run_process_with_target(self, config: _MessageQueueConfig, poll_args: dict) -> None:
        self._factory.app_processor_role.run_process(config=config, poll_args=poll_args)


    def run(self, config: _MessageQueueConfig, poll_args: dict) -> None:

        def _run_process(target):
            _data = super(MessageQueueCrawler, self).run(target=target)
            self._Running_Result.append(_data)

        _run_callback = self._format_callback(callback=_run_process)
        poll_args["callback"] = _run_callback
        self._run_process_with_target(config=config, poll_args=poll_args)


    def run_result(self) -> list:
        return self._Running_Result


    def run_and_save(self, config: _MessageQueueConfig, poll_args: dict) -> None:

        def _run_and_save_process(target):
            _data = super(MessageQueueCrawler, self).run(target=target)
            for _data_row in _data:
                self.persist(data=_data_row)

        _run_callback = self._format_callback(callback=_run_and_save_process)
        poll_args["callback"] = _run_callback
        self._run_process_with_target(config=config, poll_args=poll_args)


    def run_and_back_to_middle(self,
                               processor_config: _MessageQueueConfig, poll_args: dict,
                               back_config: _MessageQueueConfig, send_args: dict) -> None:

        def _run_and_back_function(target) -> None:
            _data = super(MessageQueueCrawler, self).run(target=target)
            for _data_row in _data:
                self.send_to_app_integration_middle_component(config=back_config, send_args=send_args, data=_data_row)

        _run_callback = self._format_callback(callback=_run_and_back_function)
        poll_args["callback"] = _run_callback
        self._run_process_with_target(config=processor_config, poll_args=poll_args)


    def _format_callback(self, callback: Callable) -> Callable:
        _role = cast(_BaseConsumer, self._factory.app_processor_role)
        _run_callback = _role.format_callback(callback=callback)
        return _run_callback


    def send_to_app_integration_middle_component(self, config: _MessageQueueConfig, send_args: dict, data: Iterable) -> None:
        _data = self._factory.data_handling_before_back.process(data=data)
        _source_role = cast(_BaseProducer, self._factory.app_source_role)

        _send_args = self._set_message(send_args=send_args, msg=str(_data), producer_config=config)
        _source_role.run_process(config=config, send_args=_send_args)


    def data_parameters(self, data: dict) -> Dict[str, Any]:
        _method = data["http_method"]
        _url = data["url"]
        _kwargs = {
            "method": _method,
            "url": _url
        }
        return _kwargs


    def _set_message(self, send_args: dict, msg: str, producer_config: _MessageQueueConfig) -> dict:
        _sending_arguments = {}
        _send_keys = send_args.keys()

        if "value" in _send_keys:
            # For Kafka
            send_args["value"] = msg
            _sending_arguments = producer_config.send_arguments(**send_args)
        elif "body" in _send_keys:
            # For RabbitMQ, ActiveMQ
            send_args["body"] = msg
            _sending_arguments = producer_config.send_arguments(**send_args)
        else:
            raise ValueError(f"The parameters are incorrect. Current parameters are: {send_args}")

        return _sending_arguments

