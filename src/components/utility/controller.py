from typing import Dict

from sqlalchemy.orm import scoped_session

from src.components.model import BaseController
from src.components.utility.service import UtilityService
from src.handler.model import Handler, HandlerResponse


class Utility(BaseController):
    """
    Controller class for utility functions in the application.

    Attributes:
        db_session (Any): The database session.
        service (UtilityService): An instance of the UtilityService.

    Methods:
        __init__(self, db_session):
            Initializes a Utility instance.
        previous_menu_item(handler, **kwargs):
            Returns the previous menu item.

    """

    def __init__(self, db_session: scoped_session) -> None:
        """
        Initializes a Utility instance.

        Args:
            db_session (Any): The database session.

        """
        super().__init__()
        self.db_session = db_session
        self.service = UtilityService()

    @staticmethod
    def previous_menu_item(
        handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Returns the previous menu item.

        Args:
            handler (Handler): The current handler.
            **kwargs: Additional arguments.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.

        """
        result = HandlerResponse()
        result.parent = handler.parent
        return result
