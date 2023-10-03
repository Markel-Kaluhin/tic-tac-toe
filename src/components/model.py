from typing import List, Type


class BaseController:
    """
    Base class for controllers in the application.

    Attributes:
        __metadata (List): A list to hold metadata of controllers.

    Methods:
        __init_subclass__(cls):
            Adds the subclass to the metadata list and sets the database session.
        metadata(self):
            Gets the metadata list containing subclasses.

    """

    __metadata: List = []

    def __init_subclass__(cls) -> None:
        """
        Adds the subclass to the metadata list and sets the database session.

        Returns:
            None

        """
        cls.__metadata.append(cls)

    @property
    def metadata(self) -> List[Type]:
        """
        Gets the metadata list containing subclasses.

        Returns:
            List: A list of subclasses.

        """
        return self.__metadata
