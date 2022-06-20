from typing import List
from abc import ABC


class BaseController(ABC):
    __metadata: List = []

    def __init_subclass__(cls, db_session=None):
        cls.db_session = db_session
        cls.__metadata.append(cls)
        return cls

    @property
    def metadata(self):
        return self.__metadata
