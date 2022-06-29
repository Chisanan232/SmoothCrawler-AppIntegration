from appintegration.role.framework import ApplicationIntegrationRole
from appintegration.task.framework import ApplicationIntegrationTask
from appintegration.components import DataHandlerBeforeBack
from appintegration.factory import ApplicationIntegrationFactory

from smoothcrawler.components.data import T
from smoothcrawler.components import HTTP, BaseHTTPResponseParser, BaseDataHandler, PersistenceFacade
from smoothcrawler.factory import FactoryTypeError
from typing import Iterable, Callable, Any, Union, Optional, TypeVar, Generic
from abc import ABCMeta, abstractmethod
import traceback
import pytest


_ApplicationIntegrationFactory = TypeVar("_ApplicationIntegrationFactory", bound=ApplicationIntegrationFactory)


class SpyHTTP(HTTP):
    pass


class SpyHTTPResponseParser(BaseHTTPResponseParser):

    def get_status_code(self, response) -> int:
        pass


class SpyDataHandler(BaseDataHandler):

    def process(self, result) -> Generic[T]:
        pass


class SpyPersistenceFacade(PersistenceFacade):

    def save(self, data: Union[Iterable, Any], *args, **kwargs) -> Generic[T]:
        pass


class SpyAppRole(ApplicationIntegrationRole):

    def _init(self, *args, **kwargs) -> Any:
        pass

    def run_process(self) -> Optional[Any]:
        pass

    def _close(self) -> None:
        pass


class SpyDataHandlerBeforeBack(DataHandlerBeforeBack):
    pass


class DummyTask(ApplicationIntegrationTask):

    def init(self, *args, **kwargs) -> Any:
        pass

    def close(self) -> None:
        pass


class FakeHTTP: pass
class FakeHTTPResponseParser: pass
class FakeDataHandler: pass
class FakePersistenceFacade: pass
class FakeAppRole: pass
class FakeDataHandlerBeforeBack: pass


class FactoryTestSpec(metaclass=ABCMeta):
    """
    Spec of testing items about module *appintegration.factory*
    """

    @abstractmethod
    @pytest.fixture(scope="class")
    def factory(self) -> Generic[_ApplicationIntegrationFactory]:
        """
        Which object should this class would test for.

        :return: An instance of ApplicationIntegrationFactory type sub-class object.
        """

        pass


    @abstractmethod
    def test_http_req_sender(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *http_factory* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_http_req_sender(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *http_factory* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_http_resp_parser(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *parser_factory* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_http_resp_parser(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *parser_factory* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_data_process(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *data_handling_factory* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_data_process(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *data_handling_factory* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_persistence_facade(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *persistence_factory* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_persistence_facade(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *persistence_factory* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_app_processor_role(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *app_processor_role* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_app_processor_role(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *app_processor_role* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_app_source_role(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *app_source_role* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_app_source_role(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *app_source_role* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_data_handler_before_back(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for property *data_handling_before_back* operations (getter and setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_set_incorrect_data_handler_before_back(self, factory: _ApplicationIntegrationFactory) -> None:
        """
        Test for assigning an incorrect type object to property *data_handling_before_back* (setter).

        :param factory: The instance of function *factory* return value in current class.
        :return: None
        """

        pass


    @staticmethod
    def _run_setting_incorrect_obj_test(setting_function: Callable) -> None:
        """
        Run the option *setting_function* and check whether the running result is correct or not.

        :param setting_function: A callable object. It's a function which would instantiate
                                               needed object and assign it into mapping property of object
                                               'ApplicationIntegrationFactory'.
        :return: None
        """

        try:
            setting_function()
        except Exception as e:
            assert True and type(e) is FactoryTypeError, "It should raise an exception 'FactoryTypeError' if it be set an incorrect type object."
        else:
            assert False, "It should NOT work finely if it be set an incorrect type object."



class TestFactory(FactoryTestSpec):

    @pytest.fixture(scope="class")
    def factory(self) -> Generic[_ApplicationIntegrationFactory]:
        return ApplicationIntegrationFactory()


    def test_http_req_sender(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_http = SpyHTTP()
        try:
            # # Test for getting
            factory.http_factory = _spy_http
            # # Test for setting
            _http_req_sender = factory.http_factory
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _http_req_sender is _spy_http, "The instances should be the same."


    def test_set_incorrect_http_req_sender(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_http_sender():
            _fake_http = FakeHTTP()
            factory.http_factory = _fake_http

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_http_sender)


    def test_http_resp_parser(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_http_resp_parser = SpyHTTPResponseParser()
        try:
            # # Test for getting
            factory.parser_factory = _spy_http_resp_parser
            # # Test for setting
            _http_resp_parser = factory.parser_factory
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _http_resp_parser is _spy_http_resp_parser, "The instances should be the same."


    def test_set_incorrect_http_resp_parser(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_http_resp_parser():
            _fake_http_resp_parser = FakeHTTPResponseParser()
            factory.parser_factory = _fake_http_resp_parser

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_http_resp_parser)


    def test_data_process(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_data_handler = SpyDataHandler()
        try:
            # # Test for getting
            factory.data_handling_factory = _spy_data_handler
            # # Test for setting
            _data_handler = factory.data_handling_factory
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _data_handler is _spy_data_handler, "The instances should be the same."


    def test_set_incorrect_data_process(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_data_handler():
            _fake_data_handler = FakeDataHandler()
            factory.data_handling_factory = _fake_data_handler

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_data_handler)


    def test_persistence_facade(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_persistence_facade = SpyPersistenceFacade()
        try:
            # # Test for getting
            factory.persistence_factory = _spy_persistence_facade
            # # Test for setting
            _persistence_facade = factory.persistence_factory
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _persistence_facade is _spy_persistence_facade, "The instances should be the same."


    def test_set_incorrect_persistence_facade(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_persistence_facade():
            _fake_persistence_facade = FakePersistenceFacade()
            factory.persistence_factory = _fake_persistence_facade

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_persistence_facade)


    def test_app_processor_role(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_app_role = SpyAppRole(task=DummyTask())
        try:
            # # Test for getting
            factory.app_processor_role = _spy_app_role
            # # Test for setting
            _app_role = factory.app_processor_role
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _app_role is _spy_app_role, "The instances should be the same."


    def test_set_incorrect_app_processor_role(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_app_role():
            _fake_app_role = FakeAppRole()
            factory.app_processor_role = _fake_app_role

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_app_role)


    def test_app_source_role(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_app_role = SpyAppRole(task=DummyTask())
        try:
            # # Test for getting
            factory.app_source_role = _spy_app_role
            # # Test for setting
            _app_role = factory.app_source_role
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _app_role is _spy_app_role, "The instances should be the same."


    def test_set_incorrect_app_source_role(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_app_role():
            _fake_app_role = FakeAppRole()
            factory.app_source_role = _fake_app_role

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_app_role)


    def test_data_handler_before_back(self, factory: _ApplicationIntegrationFactory) -> None:
        _spy_data_handler = SpyDataHandlerBeforeBack()
        try:
            # # Test for getting
            factory.data_handling_before_back = _spy_data_handler
            # # Test for setting
            _data_handler = factory.data_handling_before_back
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert _data_handler is _spy_data_handler, "The instances should be the same."


    def test_set_incorrect_data_handler_before_back(self, factory: _ApplicationIntegrationFactory) -> None:

        def _set_app_role():
            _fake_app_role = FakeDataHandlerBeforeBack()
            factory.data_handling_before_back = _fake_app_role

        FactoryTestSpec._run_setting_incorrect_obj_test(setting_function=_set_app_role)

