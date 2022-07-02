from smoothcrawler.urls import (
    # The options for the URL generating
    OPTION_VAR_INDEX, OPTION_VAR_DATE, OPTION_VAR_DATETIME, OPTION_VAR_ITERATOR,
    # The operation for setting option of URL generating
    get_option, set_index_rule, set_date_rule, set_datetime_rule, set_iterator_rule,
    # The object for extending
    URL as _URL)
from typing import Iterable, Any, Union, Optional
from abc import ABC, abstractmethod
import json
import re

from .task.messagequeue import MessageQueueConfig as _MessageQueueConfig
from .role.framework import ApplicationIntegrationRole as _ApplicationIntegrationRole
from .role.source import CrawlerSource, CrawlerProducer


OPTION_VAR_INDEX = OPTION_VAR_INDEX
OPTION_VAR_DATE = OPTION_VAR_DATE
OPTION_VAR_DATETIME = OPTION_VAR_DATETIME
OPTION_VAR_ITERATOR = OPTION_VAR_ITERATOR

get_option = get_option
set_index_rule = set_index_rule
set_date_rule = set_date_rule
set_datetime_rule = set_datetime_rule
set_iterator_rule = set_iterator_rule


class HTTPMethodIsInvalidError(ValueError):

    def __str__(self):
        return "The HTTP method is invalid. Please refer to RFC 2616 page 36 to use valid HTTP method."


class API:

    _API_Info: dict = {
        "http_method": "GET",
        "url": None,
        "parameters": {},
        "body": None,
        "content_type": None,
    }


    @property
    def info(self) -> dict:
        return self._API_Info


    @property
    def http_method(self) -> str:
        """
        HTTP method. Refer to RFC 2616, you could use GET, POST, PUT, DELETE, etc.

        :return: A string type value.
        """

        return self._API_Info.get("http_method")


    @http_method.setter
    def http_method(self, http_method: str) -> None:
        if re.search("get", http_method, re.IGNORECASE) or \
                re.search("post", http_method, re.IGNORECASE) or \
                re.search("put", http_method, re.IGNORECASE) or \
                re.search("delete", http_method, re.IGNORECASE) or \
                re.search("head", http_method, re.IGNORECASE) or \
                re.search("option", http_method, re.IGNORECASE) or \
                re.search("trace", http_method, re.IGNORECASE) or \
                re.search("connect", http_method, re.IGNORECASE):
            self._API_Info["http_method"] = http_method
        else:
            raise HTTPMethodIsInvalidError


    @property
    def url(self) -> str:
        """
        URL.

        :return: A string type value.
        """

        return self._API_Info.get("url")


    @url.setter
    def url(self, url: str) -> None:
        if type(url) is not str:
            raise ValueError("URL value should be a string type value.")
        self._API_Info["url"] = url


    @property
    def parameters(self) -> dict:
        """
        Parameters of the HTTP request.

        :return: A dict type value.
        """

        return self._API_Info.get("parameters")


    @parameters.setter
    def parameters(self, parameters: dict) -> None:
        if type(parameters) is not dict:
            raise ValueError("Parameters value should be a dict type value.")
        self._API_Info["parameters"] = parameters


    @property
    def body(self) -> Any:
        """
        The body of HTTP request.

        :return: An Any type value.
        """

        return self._API_Info.get("body")


    @body.setter
    def body(self, body: Any) -> None:
        self._API_Info["body"] = body


    @property
    def content_type(self) -> str:
        """
        Content type of HTTP request.

        :return: A string type value.
        """

        return self._API_Info.get("content_type")


    @content_type.setter
    def content_type(self, content_type: str) -> None:
        if type(content_type) is not str:
            raise ValueError("Content-Type value should be a string type value.")
        self._API_Info["content_type"] = content_type



class ApplicationIntegrationURL(_URL, ABC):

    def __init__(self, role: _ApplicationIntegrationRole, base: str, start: Optional[Union[int, str]] = None, end: Optional[Union[int, str]] = None, formatter: str = "yyyymmdd", iter: Optional[Iterable] = None):
        super(ApplicationIntegrationURL, self).__init__(base=base, start=start, end=end, formatter=formatter, iter=iter)
        self._role = role
        self._http_info: API = API()


    def set_http_info(self, info: API) -> None:
        self._http_info = info


    @abstractmethod
    def _format_data(self, urls: Iterable[str]) -> Iterable[Iterable]:
        pass



class FileBasedURL(ApplicationIntegrationURL):

    def generate(self) -> None:
        _urls = super(FileBasedURL, self).generate()
        _api_info = self._format_data(urls=_urls)
        self._role.run_process(data=_api_info)


    def _format_data(self, urls: Iterable[str]) -> Iterable[Iterable]:
        _all_api_info = []
        for _url in urls:
            _api_info = [_url, self._http_info.http_method, self._http_info.parameters, self._http_info.body, self._http_info.content_type]
            _all_api_info += [_api_info]
        return _all_api_info



class MessageQueueURLProducer(ApplicationIntegrationURL):

    def __init__(self, role: _ApplicationIntegrationRole, base: str, start: Optional[Union[int, str]] = None, end: Optional[Union[int, str]] = None, formatter: str = "yyyymmdd", iter: Optional[Iterable] = None):
        super(MessageQueueURLProducer, self).__init__(role=role, base=base, start=start, end=end, formatter=formatter, iter=iter)

        self._producer_config: _MessageQueueConfig = None
        self._send_args: dict = {}


    @property
    def producer_config(self) -> _MessageQueueConfig:
        return self._producer_config


    @property
    def send_args(self) -> dict:
        return self._send_args


    def set_producer(self, producer_config: _MessageQueueConfig, send_args: dict) -> None:
        self._producer_config = producer_config
        self._send_args = send_args


    def generate(self) -> None:
        _urls = super(MessageQueueURLProducer, self).generate()
        _data = self._format_data(urls=_urls)
        for _data_row in _data:
            # Update the value or body as the data row.
            _send_arguments = self._set_message(msg=_data_row)
            self._role.run_process(config=self._producer_config, send_args=_send_arguments)


    def _format_data(self, urls: Iterable[str]) -> Iterable:
        _all_api_info = []
        for _url in urls:
            self._http_info.url = _url
            _json_data = json.dumps(self._http_info.info)
            _all_api_info.append(_json_data)
        return _all_api_info


    def _set_message(self, msg: str) -> dict:
        _sending_arguments = {}
        _send_keys = self._send_args.keys()

        if "value" in _send_keys:
            # For Kafka
            self._send_args["value"] = msg
            _sending_arguments = self._producer_config.send_arguments(**self._send_args)
        elif "body" in _send_keys:
            # For RabbitMQ, ActiveMQ
            self._send_args["body"] = msg
            _sending_arguments = self._producer_config.send_arguments(**self._send_args)
        else:
            raise ValueError(f"The parameters are incorrect. Current parameters are: {self._send_args}")

        return _sending_arguments

