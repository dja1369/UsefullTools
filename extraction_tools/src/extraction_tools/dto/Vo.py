from pydantic import BaseModel


class HostInformation(BaseModel):
    host_ip: str
    host_name: str
    host_password: str

class DatabaseInformation(BaseModel):
    db_user: str
    db_password: str
    db_name: str
    db_port: int