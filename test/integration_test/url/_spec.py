from appintegration.url import ApplicationIntegrationURL

from ..._data import Test_URLs_List

from typing import TypeVar, Generic, Iterable
from abc import ABCMeta, abstractmethod
import traceback
import pytest


_ApplicationIntegrationURL = TypeVar("_ApplicationIntegrationURL", bound=ApplicationIntegrationURL)


class ApplicationIntegrationURLTestSpec(metaclass=ABCMeta):

    @pytest.fixture(scope="class")
    @abstractmethod
    def url(self) -> Generic[_ApplicationIntegrationURL]:
        pass


    def test_set_http_info(self) -> None:
        pass


    def test_format_data(self, url: _ApplicationIntegrationURL) -> None:
        try:
            _formatted_urls = url._format_data(urls=Test_URLs_List)
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            self._chk_format_data_running_result(urls=_formatted_urls)


    @abstractmethod
    def _chk_format_data_running_result(self, urls: Iterable[Iterable]) -> None:
        pass


    def test_generate(self, url: _ApplicationIntegrationURL) -> None:
        try:
            url.generate()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            self._chk_generate_running_result(url_inst=url)


    @abstractmethod
    def _chk_generate_running_result(self, url_inst: _ApplicationIntegrationURL) -> None:
        pass