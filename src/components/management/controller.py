from typing import Dict

from sqlalchemy.orm import scoped_session

from src.components.management.service import ManagementService
from src.components.model import BaseController
from src.database.model.user import User
from src.handler.model import Handler, HandlerResponse


class Management(BaseController):
    """
    Controller class for managing user data and functionalities.

    Attributes:
        db_session (scoped_session): The database session.
        service (ManagementService): An instance of the ManagementService.

    Methods:
        __init__(self, db_session):
            Initializes a Management instance.
        player_details(self, handler, **kwargs):
            Display detailed information of one user.
        player_list(self, handler, **kwargs):
            Display a list of users with an option to view detailed information.
        player_create(self, handler, **kwargs):
            Create a new user.
        player_delete(self, handler, **kwargs):
            Display a list of users with an option to delete a user.
        player_delete_confirmation(self, handler, **kwargs):
            Confirm deletion of a user.
        new_league_season(self, handler, **kwargs):
            Create a new league season.
    """

    def __init__(self, db_session: scoped_session) -> None:
        """
        Initializes a Management instance.

        Args:
            db_session (Any): The database session.
        """
        super().__init__()
        self.db_session = db_session
        self.service = ManagementService(self.db_session)

    def player_details(
        self, handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Display detailed information of one user.

        Args:
            handler (Handler): The handler from which this handler was called.
            kwargs (dict): Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.
        """

        user: User = kwargs["user"]  # type: ignore [assignment]

        self.service.show_player_details(user)

        return HandlerResponse()

    def player_list(
        self, handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Display a list of users with an option to view detailed information.

        Args:
            handler (Handler): The handler from which this handler was called.
            kwargs (dict): Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Choose one to see detail.
        Player table:
        """
        )

        result = self.service.show_player_list(handler, Management, "player_details")

        return HandlerResponse(dynamic_menu_items=result)

    def player_create(
        self, handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Create a new user.

        Args:
            handler (Handler): The handler from which this handler was called.
            kwargs (dict): Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.
        """

        self.service.player_create()

        return HandlerResponse()

    def player_delete(
        self, handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Display a list of users with an option to delete a user.

        Args:
            handler (Handler): The handler from which this handler was called.
            kwargs (dict): Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Choose one to delete.
        Player list:
        """
        )

        result = self.service.show_player_list(handler, Management, "player_delete_confirmation")

        return HandlerResponse(dynamic_menu_items=result)

    def player_delete_confirmation(
        self, handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Confirm deletion of a user.

        Args:
            handler (Handler): The handler from which this handler was called.
            kwargs (dict): Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.
        """
        user: User = kwargs["user"]  # type: ignore [assignment]

        decision = input("Are you sure? y/N")
        if decision == "y":
            self.db_session.delete(user)
            self.db_session.commit()
            print(f"User {user.nickname} was deleted")
        return HandlerResponse()

    def new_league_season(
        self, handler: Handler, **kwargs: Dict[str, str]  # pylint: disable=unused-argument
    ) -> HandlerResponse:
        """
        Create a new league season.

        Args:
            handler (Handler): The handler from which this handler was called.
            kwargs (dict): Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: An object containing data to run the next handlers or generated dynamic handlers.
        """

        self.service.create_new_league_season()

        return HandlerResponse()
