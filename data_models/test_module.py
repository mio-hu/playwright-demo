from data_models import *
from dataclasses import dataclass

@dataclass
class CreateUser(BaseDataClass):
    username: str = ""
    password: str = ""