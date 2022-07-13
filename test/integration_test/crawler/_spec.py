from smoothcrawler_appintegration.role.framework import ApplicationIntegrationRole
from smoothcrawler_appintegration.task.framework import ApplicationIntegrationTask
from smoothcrawler_appintegration.crawler import AppIntegrationCrawler
from smoothcrawler_appintegration.factory import ApplicationIntegrationFactory

from ._components import RequestsHTTPRequest, RequestsStockHTTPResponseParser, ExampleWebDataHandler, DataFilePersistenceLayer, StockDataHandlerBeforeBack

from typing import Iterable, TypeVar, Generic
from abc import ABCMeta, abstractmethod
import pytest


_ApplicationIntegrationRole = TypeVar("_ApplicationIntegrationRole", bound=ApplicationIntegrationRole)
_ApplicationIntegrationTask = TypeVar("_ApplicationIntegrationTask", bound=ApplicationIntegrationTask)
_AppIntegrationCrawler = TypeVar("_AppIntegrationCrawler", bound=AppIntegrationCrawler)
_ApplicationIntegrationFactory = TypeVar("_ApplicationIntegrationFactory", bound=ApplicationIntegrationFactory)


class CrawlerTestSpec(metaclass=ABCMeta):
    """
    Test spec for testing object which is sub-class of **AppIntegrationCrawler** in module *crawler*.
    """

    @pytest.fixture(scope="class")
    def factory(self) -> _ApplicationIntegrationFactory:
        """
        Initial object **ApplicationIntegrationFactory** and set the instances.

        :return: An instance of object **ApplicationIntegrationFactory** which saves
                      some instances to let *crawler* to use in running process.
        """

        _factory = ApplicationIntegrationFactory()
        _factory.http_factory = RequestsHTTPRequest()
        _factory.parser_factory = RequestsStockHTTPResponseParser()
        _factory.data_handling_factory = ExampleWebDataHandler()
        _factory.persistence_factory = DataFilePersistenceLayer()
        _factory.app_processor_role = self.processor_role()
        _factory.app_source_role = self.source_role()
        _factory.data_handling_before_back = StockDataHandlerBeforeBack()
        return _factory


    @abstractmethod
    def processor_role(self) -> Generic[_ApplicationIntegrationRole]:
        """
        Which type of *application processor role* to use in crawler testing.

        :return: An instance of object **ApplicationIntegrationRole**.
        """

        pass


    @abstractmethod
    def task(self, **kwargs) -> Generic[_ApplicationIntegrationTask]:
        """
        Which task it would be used by *role* (*application source* or *application processor*)
        to run testing.

        :param kwargs: Some parameters for different type object **ApplicationIntegrationTask**.
        :return: An instance of object **ApplicationIntegrationTask**
        """

        pass


    @abstractmethod
    def source_role(self) -> Generic[_ApplicationIntegrationRole]:
        """
        Which type of *application source role* to use in testing or for crawler's method *run_and_back_to_middle*.

        :return: An instance of object **ApplicationIntegrationRole**.
        """

        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def crawler(self, factory: _ApplicationIntegrationFactory) -> Generic[_AppIntegrationCrawler]:
        """
        Which *crawler* should be test and it would be initial with **ApplicationIntegrationFactory**.

        :param factory: An instance of object **ApplicationIntegrationFactory** which has saved some factories.
        :return: An instance of object **AppIntegrationCrawler**.
        """

        pass


    @abstractmethod
    def test_run_process_with_target(self, crawler: Generic[_AppIntegrationCrawler]) -> None:
        """
        Test for getting targets for crawler to run with it.

        :param crawler: The instance of object **AppIntegrationCrawler**.
        :return: None
        """

        pass


    @abstractmethod
    def _chk_result_of_running_process_with_target(self, **kwargs) -> None:
        """
        Checking the running result of getting targets.

        :param _targets: An iterable object which saves info like URLs, HTTP method, etc about targets.
        :return: None
        """

        pass


    @abstractmethod
    def test_run(self, crawler: Generic[_AppIntegrationCrawler]) -> None:
        """
        Test for running crawler generally and get the result.

        :param crawler: The instance of object **AppIntegrationCrawler**.
        :return: None
        """

        pass


    @abstractmethod
    def _chk_result_of_running(self, _results: Iterable) -> None:
        """
        Checking the running result of running crawler.

        :param _results: The results data of running crawler.
        :return: None
        """

        pass


    @abstractmethod
    def test_run_and_save(self, crawler: Generic[_AppIntegrationCrawler]) -> None:
        """
        Test for running crawler and save the result data.

        :param crawler: The instance of object **AppIntegrationCrawler**.
        :return:
        """

        pass


    @abstractmethod
    def _chk_result_of_running_and_saving(self, _factory) -> None:
        """
        Checking the running result of crawler running and saving.

        :param _factory: The instance of using factory **ApplicationIntegrationFactory**.
        :return: None
        """

        pass


    @abstractmethod
    def test_run_and_back_to_middle(self, crawler: Generic[_AppIntegrationCrawler]) -> None:
        """
        Test for running crawler and let the result data back to application integration middle system.

        :param crawler: The instance of object **AppIntegrationCrawler**.
        :return:
        """

        pass


    @abstractmethod
    def _chk_result_of_running_and_backing_to_middle(self) -> None:
        """
        Check the running result of crawler running and let result data back to application integration middle system.

        :return: None
        """

        pass


    @abstractmethod
    def _prepare_target_data(self) -> None:
        """
        Prepare the data for testing running.

        :return: None
        """

        pass


    @abstractmethod
    def _final_process(self) -> None:
        """
        Do something finally in testing process.

        :return: None
        """

        pass

