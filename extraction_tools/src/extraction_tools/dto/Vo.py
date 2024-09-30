from pydantic import BaseModel

class HostInformation(BaseModel):
    ip: str
    name: str
    password: str

class DatabaseInformation(BaseModel):
    host_ip: str
    user: str
    password: str
    db_name: str
    port: int