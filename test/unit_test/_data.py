from typing import List, Dict


Test_Data_List: List = [
    ["http://www.example.com", "GET"],
    ["http://www.example.com", "POST"],
    ["http://www.example.com", "PUT"]
]

Test_JSON_Data: Dict = {"data": [
    ["http://www.example.com", "GET"],
    ["http://www.example.com", "POST"],
    ["http://www.example.com", "PUT"]
]}

Test_Error_Data_List: List = [
    ["http://www.example.com", "GET"],
    ["http://www.example.com", "POST"],
    ["http://www.example.com", "PUT"],
    "error"
]

