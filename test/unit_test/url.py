from appintegration.url import (
    OPTION_VAR_DATE, API, HTTPMethodIsInvalidError,
    ApplicationIntegrationURL, FileBasedURL, MessageQueueURLProducer
)

from ._dummy_objs import (
    # For recording testing state
    _get_role_processes_list, _get_task_processes_list, _reset_processes_list, RoleProcess, TaskProcess,
    # For some dummy objects for running test
    DummySource, DummyProducer, DummySourceTask, DummyMsgQueueConfig, _Dummy_Arguments
)
from .._config import Test_HTTP_Parameters, Test_HTTP_Body, Test_HTTP_Content_Type
from .._data import Test_URL, Test_URLs_List

from typing import Iterable, TypeVar, Generic, Union
from abc import ABCMeta, abstractmethod
import traceback
import pytest
import json


_API = TypeVar("_API", bound=API)
_ApplicationIntegrationURL = TypeVar("_ApplicationIntegrationURL", bound=ApplicationIntegrationURL)


class APITestSpec(metaclass=ABCMeta):
    """
    Test spec for testing object **API** in module *url*.
    """

    @pytest.fixture(scope="function")
    @abstractmethod
    def api(self) -> Generic[_API]:
        """
        Which object it would test for. It's the instance of object *API* here.

        :return: An instance of object *API*.
        """

        pass


    @abstractmethod
    def test_http_method(self, api: _API) -> None:
        """
        Test for getting and setting attribute *HTTP method*.

        :param api: An instance of object *API* for testing.
        :return: None
        """

        pass


    @abstractmethod
    def test_url(self, api: _API) -> None:
        """
        Test for getting and setting attribute *URL*.

        :param api: An instance of object *API* for testing.
        :return: None
        """

        pass


    @abstractmethod
    def test_parameters(self, api: _API) -> None:
        """
        Test for getting and setting attribute *parameters*.

        :param api: An instance of object *API* for testing.
        :return: None
        """

        pass


    @abstractmethod
    def test_body(self, api: _API) -> None:
        """
        Test for getting and setting attribute *body*.

        :param api: An instance of object *API* for testing.
        :return: None
        """

        pass


    @abstractmethod
    def test_content_type(self, api: _API) -> None:
        """
        Test for getting and setting attribute *Content-Type*.

        :param api: An instance of object *API* for testing.
        :return: None
        """

        pass



class TestAPI(APITestSpec):

    @pytest.fixture(scope="function")
    def api(self) -> Generic[_API]:
        return API()


    @pytest.mark.parametrize("method", ["get", "post", "put", "delete", "option", "head", "trace", "connect", "yee"])
    def test_http_method(self, api: _API, method: str) -> None:
        try:
            api.http_method = method
            assert api.http_method == method, f"Its value should be same as input value {method}."
        except Exception as e:
            if type(e) is HTTPMethodIsInvalidError:
                assert True, "It works finely."
            else:
                assert False, "It should raise an exception *HTTPMethodIsInvalidError*."


    def test_url(self, api: _API) -> None:
        try:
            api.url = Test_URL
            assert api.url == Test_URL, f"Its value should be same as input value {Test_URL}."
        except Exception as e:
            if type(e) is ValueError:
                assert True, "It works finely."
            else:
                assert False, "It should raise an exception *ValueError*."


    def test_parameters(self, api: _API) -> None:
        try:
            api.parameters = Test_HTTP_Parameters
            assert api.parameters == Test_HTTP_Parameters, f"Its value should be same as input value {Test_HTTP_Parameters}."
        except Exception as e:
            if type(e) is ValueError:
                assert True, "It works finely."
            else:
                assert False, "It should raise an exception *ValueError*."


    def test_body(self, api: _API) -> None:
        try:
            api.body = Test_HTTP_Body
            assert api.body == Test_HTTP_Body, f"Its value should be same as input value {Test_HTTP_Body}."
        except Exception:
            assert False, "It should NOT raise any exception when it sets HTTP body value."


    def test_content_type(self, api: _API) -> None:
        try:
            api.content_type = Test_HTTP_Content_Type
            assert api.content_type == Test_HTTP_Content_Type, f"Its value should be same as input value {Test_HTTP_Content_Type}."
        except Exception as e:
            if type(e) is ValueError:
                assert True, "It works finely."
            else:
                assert False, "It should raise an exception *ValueError*."



class ApplicationIntegrationURLTestSpec(metaclass=ABCMeta):
    """
    Test spec for testing object **ApplicationIntegrationURL** in module *url*.
    """

    @pytest.fixture(scope="class")
    @abstractmethod
    def url(self) -> Generic[_ApplicationIntegrationURL]:
        """
        Which object for testing. It should be an instance of sub-class of object **ApplicationIntegrationURL**.

        :return: An instance of sub-class object **ApplicationIntegrationURL**.
        """

        pass


    @property
    @abstractmethod
    def role(self) -> Union[DummySource, DummyProducer]:
        """
        Which object it should be used with **ApplicationIntegrationURL**. In SmoothCrawler AppIntegration realm,
        **ApplicationIntegrationURL** is a source application. So it should be used with one specific
        **ApplicationIntegrationRole**.

        :return: An instance of one specific object which is sub-class of **ApplicationIntegrationRole**.
        """

        pass


    @pytest.fixture(scope="function")
    def api_info(self) -> API:
        """
        API instance which saves some info.

        :return: An instance of object **API**.
        """

        return API()


    @property
    def _procedure_steps_number(self) -> int:
        """
        The count of steps in an entire procedure of running **ApplicationIntegrationRole** with **ApplicationIntegrationTask**.
        In generally, it would run as initial -> do something (read/consume or write/produce) -> close.

        :return: An integer **3**.
        """

        return 3


    def test_set_http_info(self, url: _ApplicationIntegrationURL, api_info: API) -> None:
        """
        Testing for setting HTTP info via object **API**.

        :param url: The instance which is **ApplicationIntegrationURL** type.
        :param api_info: The instance of object **API**.
        :return: None
        """

        url.set_http_info(info=api_info)
        assert url._http_info == api_info, "These objects should be the same."


    def test_format_data(self, url: _ApplicationIntegrationURL, api_info: API) -> None:
        """
        Testing for formatting data by **ApplicationIntegrationURL**.

        :param url: The instance which is **ApplicationIntegrationURL** type.
        :param api_info: The instance of object **API**.
        :return: None
        """

        try:
            _formatted_urls = url._format_data(urls=Test_URLs_List)
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            self._chk_format_data_running_result(urls=_formatted_urls, api_info_inst=api_info)


    @abstractmethod
    def _chk_format_data_running_result(self, urls: Iterable[Iterable], api_info_inst: API) -> None:
        """
        Check the running result of formatting data.

        :param urls: The iterable object which saves URLs info.
        :param api_info_inst: The instance of object **API**.
        :return: None
        """

        pass


    def test_generate(self, url: _ApplicationIntegrationURL, api_info: API) -> None:
        """
        Testing for generating (write/send/produce) URLs by **ApplicationIntegrationURL**.

        :param url: The instance which is **ApplicationIntegrationURL** type.
        :param api_info: The instance of object **API**.
        :return: None
        """

        _reset_processes_list()

        try:
            url.generate()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            self._chk_generate_running_result(url_inst=url)


    @abstractmethod
    def _chk_generate_running_result(self, url_inst: _ApplicationIntegrationURL) -> None:
        """
        Check the running result of generating URLs.

        :param url_inst: The instance which is **ApplicationIntegrationURL** type.
        :return:None
        """

        pass



class TestFileBasedURL(ApplicationIntegrationURLTestSpec):

    @pytest.fixture(scope="class")
    def url(self) -> FileBasedURL:
        _target_url = "http:www.test.com?date={" + OPTION_VAR_DATE + "}"
        _date_urls = FileBasedURL(role=self.role, base=_target_url, start="20220601", end="20220603", formatter="yyyymmdd")
        _date_urls.set_http_info(info=API())
        return _date_urls


    @property
    def role(self) -> DummySource:
        return DummySource(task=DummySourceTask())


    def _chk_format_data_running_result(self, urls: Iterable[Iterable], api_info_inst: API) -> None:
        assert type(urls) is list, "The data type of URLs should be list."
        for _url in urls:
            assert type(_url) is list, "The data type of each elements of URLs list should also be list."


    def _chk_generate_running_result(self, url_inst: FileBasedURL) -> None:
        _role_processes_list = _get_role_processes_list()
        _task_processes_list = _get_task_processes_list()

        assert len(_role_processes_list) == self._procedure_steps_number, f"In file based case, the steps number in procedure should be {self._procedure_steps_number} (initial(open) -> write -> close)."
        assert _role_processes_list[0] == RoleProcess.Init, "The first step should be initialization like open file IO stream."
        assert _role_processes_list[1] == RoleProcess.Write, "The second step should be write target data into file."
        assert _role_processes_list[2] == RoleProcess.Close, "The latest step (the third one) should be close the file IO stream."

        assert len(_task_processes_list) == self._procedure_steps_number, f"In file based case, the steps number in procedure should be {self._procedure_steps_number} (initial(open) -> write -> close)."
        assert _task_processes_list[0] == TaskProcess.Init, "The first step should be initialization like open file IO stream."
        assert _task_processes_list[1] == TaskProcess.Generate, "The second step should be write target data into file."
        assert _task_processes_list[2] == TaskProcess.Close, "The latest step (the third one) should be close the file IO stream."



class TestMessageQueueURL(ApplicationIntegrationURLTestSpec):

    @pytest.fixture(scope="class")
    def url(self) -> MessageQueueURLProducer:
        _target_url = "http:www.test.com?date={" + OPTION_VAR_DATE + "}"
        _date_urls = MessageQueueURLProducer(role=self.role, base=_target_url, start="20220601", end="20220603", formatter="yyyymmdd")
        _date_urls.set_http_info(info=API())
        _date_urls.set_producer(producer_config=self.producer_config, send_args=_Dummy_Arguments)
        return _date_urls


    @property
    def producer_config(self) -> DummyMsgQueueConfig:
        return DummyMsgQueueConfig()


    @property
    def role(self) -> DummyProducer:
        return DummyProducer(task=DummySourceTask())


    def test_producer_config(self, url: MessageQueueURLProducer) -> None:
        assert isinstance(url.producer_config, DummyMsgQueueConfig) is True, f"The producer configuration should be same as dummy object {self.producer_config}."


    def test_send_args(self, url: MessageQueueURLProducer) -> None:
        assert url.send_args == _Dummy_Arguments, f"The arguments should be same as inout parameters '{_Dummy_Arguments}'."


    def _chk_format_data_running_result(self, urls: Iterable[str], api_info_inst: API) -> None:
        assert type(urls) is list, "The data type of URLs should be list."
        for _url in urls:
            try:
                _json_data = json.loads(_url)
            except Exception:
                assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
            else:
                _json_data_key = _json_data.keys()
                assert _json_data_key == api_info_inst.info.keys(), "The keys of JSON type data from message queue system should be same as object *API*."


    @property
    def _procedure_steps_running_times(self) -> int:
        return 3


    def _chk_generate_running_result(self, url_inst: MessageQueueURLProducer) -> None:
        _role_processes_list = _get_role_processes_list()
        _task_processes_list = _get_task_processes_list()

        assert len(_role_processes_list) == self._procedure_steps_number * self._procedure_steps_running_times, f"In message queue case, the steps number in procedure should be {self._procedure_steps_number} (initial(build connection) -> send -> close)."
        assert len(_task_processes_list) == self._procedure_steps_number * self._procedure_steps_running_times, f"In message queue case, the steps number in procedure should be {self._procedure_steps_number} (initial(build connection) -> send -> close)."

        for _i in range(self._procedure_steps_number):
            _init_index = 0 + (self._procedure_steps_number * _i)
            _send_index = 1 + (self._procedure_steps_number * _i)
            _close_index = 2 + (self._procedure_steps_number * _i)

            assert _role_processes_list[_init_index] == RoleProcess.Init, "The first step should be initialization like building TCP connection with the message queue middle system."
            assert _role_processes_list[_send_index] == RoleProcess.Send, "The second step should be sending data to message queue middle system."
            assert _role_processes_list[_close_index] == RoleProcess.Close, "The latest step (the third one) should be close the TCP connection with message queue middle system."

            assert _task_processes_list[_init_index] == TaskProcess.Init, "The first step should be initialization like building TCP connection with the message queue middle system."
            assert _task_processes_list[_send_index] == TaskProcess.Generate, "The second step should be sending data to message queue middle system."
            assert _task_processes_list[_close_index] == TaskProcess.Close, "The latest step (the third one) should be close the TCP connection with message queue middle system."

