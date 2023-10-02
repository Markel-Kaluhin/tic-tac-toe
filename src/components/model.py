from abc import ABC  # pylint: disable=no-name-in-module
from typing import List, Optional, Type

from sqlalchemy.orm import scoped_session


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
    db_session: Optional[scoped_session] = None

    def __init_subclass__(cls, db_session: Optional[scoped_session] = None) -> None:
        """
        Adds the subclass to the metadata list and sets the database session.

        Args:
            db_session (Any): The database session.

        Returns:
            None

        """
        cls.db_session = db_session
        cls.__metadata.append(cls)

    @property
    def metadata(self) -> List[Type]:
        """
        Gets the metadata list containing subclasses.

        Returns:
            List: A list of subclasses.

        """
        return self.__metadata
