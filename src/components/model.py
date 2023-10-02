from abc import ABC  # pylint: disable=no-name-in-module
from typing import List


class BaseController(ABC):
    """
    An abstract base class for controllers in the application.

    Attributes:
        __metadata (List): A list to hold metadata of controllers.

    Methods:
        __init_subclass__(cls, db_session=None):
            Adds the subclass to the metadata list and sets the database session.
        metadata(self):
            Gets the metadata list containing subclasses.

    """

    __metadata: List = []

    def __init_subclass__(cls, db_session=None):
        """
        Adds the subclass to the metadata list and sets the database session.

        Args:
            db_session (Any): The database session.

        Returns:
            cls (Type): The subclass of BaseController.

        """
        cls.db_session = db_session
        cls.__metadata.append(cls)
        return cls

    @property
    def metadata(self):
        """
        Gets the metadata list containing subclasses.

        Returns:
            List: A list of subclasses.

        """
        return self.__metadata
