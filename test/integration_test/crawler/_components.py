from smoothcrawler_appintegration. components import DataHandlerBeforeBack
from smoothcrawler_appintegration.role import CrawlerSource
from smoothcrawler_appintegration.task import CSVTask

from ._persistence_layer import StockDao

from smoothcrawler.components.persistence import PersistenceFacade
from smoothcrawler.components.httpio import HTTP
from smoothcrawler.components.data import BaseHTTPResponseParser, BaseDataHandler
from pathlib import Path
from typing import Dict, Any
from bs4 import BeautifulSoup
import requests



class RequestsHTTPRequest(HTTP):

    __Http_Response = None

    def get(self, url: str, *args, **kwargs):
        if self.__Http_Response is None:
            self.__Http_Response = requests.get(url)
        return self.__Http_Response



class RequestsHTTPResponseParser(BaseHTTPResponseParser):

    def get_status_code(self, response: requests.Response) -> int:
        return response.status_code


    def handling_200_response(self, response: requests.Response) -> Any:
        _bs = BeautifulSoup(response.text, "html.parser")
        _example_web_title = _bs.find_all("h1")
        return _example_web_title



class RequestsStockHTTPResponseParser(BaseHTTPResponseParser):

    def get_status_code(self, response: requests.Response) -> int:
        return response.status_code


    def handling_200_response(self, response: requests.Response) -> Any:
        _data = response.json()
        return _data



class ExampleWebDataHandler(BaseDataHandler):

    def process(self, result):
        return result



class DataFilePersistenceLayer(PersistenceFacade):

    @property
    def file_path(self) -> str:
        return str(Path("./new_data.csv"))


    @property
    def mode(self) -> str:
        return "a+"


    def save(self, data, *args, **kwargs):
        _handled_data = []
        for data_row in data["data"]:
            _handled_data.append(data_row)

        _role = CrawlerSource(task=CSVTask(file=self.file_path, mode=self.mode))
        _role.run_process(data=_handled_data)



class DataDatabasePersistenceLayer(PersistenceFacade):

    def save(self, data, *args, **kwargs):
        _stock_dao = StockDao()
        _stock_dao.create_stock_data_table(stock_symbol="2330")
        _data_rows = [tuple(d) for d in data]
        _stock_dao.batch_insert(stock_symbol="2330", data=_data_rows)



class StockDataHandlerBeforeBack(DataHandlerBeforeBack):

    _First_Data_Row: int = 0

    def process(self, data: Dict) -> list:
        _handled_data = []

        if self._First_Data_Row == 0:
            _handled_data.append(data["fields"])
            self._First_Data_Row += 1

        for data_row in data["data"]:
            _handled_data.append(data_row)
        return _handled_data

