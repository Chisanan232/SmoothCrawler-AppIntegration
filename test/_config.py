from pathlib import Path


# For file based settings
Test_CSV_File_Path: str = str(Path("./for_testing.csv"))
Test_XLSX_File_Path: str = str(Path("./for_testing.xlsx"))
Test_JSON_File_Path: str = str(Path("./for_testing.json"))
Test_XML_File_Path: str = str(Path("./for_testing.xml"))
Test_PROPERTIES_File_Path: str = str(Path("./for_testing.properties"))

Test_Writing_Mode: str = "a+"
Test_XML_Writing_Mode: str = "wb"
Test_Reading_Mode: str = "r"


# For file based settings

class DummyObj:

    def __str__(self):
        return "DummyObj"

    def __repr__(self):
        return self.__str__()

    @property
    def attr(self) -> str:
        return "testing_attribute"


Test_HTTP_Parameters = {"date": "20220625", "code": "6666"}
Test_HTTP_Body = str(DummyObj())
Test_HTTP_Content_Type = "application/json"
