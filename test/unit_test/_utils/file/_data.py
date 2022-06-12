from typing import List, Dict


Test_Data_List: List = [
    ['0108-01-02 00:00:00', 32900482.0, 7276419230.0, 226.5, 226.5, 219.0, 219.5, 12329.0],
    ['0108-01-03 00:00:00', 34615620.0, 7459051790.0, 214.0, 218.0, 214.0, 215.5, 14549.0],
    ['0108-01-04 00:00:00', 67043521.0, 13987136785.0, 211.5, 211.5, 206.5, 208.0, 28786.0]
]

Test_Error_Data_List: List = [
    ['0108-01-02 00:00:00', 32900482.0, 7276419230.0, 226.5, 226.5, 219.0, 219.5, 12329.0],
    ['0108-01-03 00:00:00', 34615620.0, 7459051790.0, 214.0, 218.0, 214.0, 215.5, 14549.0],
    ['0108-01-04 00:00:00', 67043521.0, 13987136785.0, 211.5, 211.5, 206.5, 208.0, 28786.0],
    "error"
]

Test_JSON_Data: Dict = {"data": [
    ['0108-01-02 00:00:00', 32900482.0, 7276419230.0, 226.5, 226.5, 219.0, 219.5, 12329.0],
    ['0108-01-03 00:00:00', 34615620.0, 7459051790.0, 214.0, 218.0, 214.0, 215.5, 14549.0],
    ['0108-01-04 00:00:00', 67043521.0, 13987136785.0, 211.5, 211.5, 206.5, 208.0, 28786.0]
]}
