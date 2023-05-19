from pydantic import BaseModel

class BasicData(BaseModel):
    database_name: str
    db_server: str
    url_api_root: str
    url_wso2: str
    url_wso2_checker: str
