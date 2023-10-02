import sys

from mypy_extensions import KwArg
from sqlalchemy.orm import Session

from src.components.main_menu.service import MainMenuService
from src.components.model import BaseController
from src.database import delete_session
from src.handler.model import Handler, HandlerResponse


class MainMenu(BaseController):
    """
    Controller for the main menu functionalities.

    Attributes:
        db_session (Any): The database session.
        service (MainMenuService): Instance of the MainMenuService.

    Methods:
        __init__(self, db_session):
            Initializes a MainMenu instance.
        welcome(self, handler, **kwargs):
            Welcome window, shown when the application is initialized.
        management(self, handler, **kwargs):
            Navigate to the management menu.
        player_statistic(self, handler, **kwargs):
            Show statistics of past games.
        ranking_table(self, handler, **kwargs):
            Show the ranking table.
        exit_game(self, handler, **kwargs):
            Exit the game.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Initializes a MainMenu instance.

        Args:
            db_session (Any): The database session.
        """
        super().__init__()
        self.db_session = db_session
        self.service = MainMenuService(self.db_session)

    def welcome(self, handler: Handler, **kwargs: KwArg) -> HandlerResponse:  # pylint: disable=unused-argument
        """
        Welcome window, shown when the application is initialized.

        Args:
            handler: The handler from which this handler was called.
            kwargs: Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: Object with stored data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Greeting player. Choose the option:
        """
        )
        return HandlerResponse()

    def management(self, handler: Handler, **kwargs: KwArg) -> HandlerResponse:  # pylint: disable=unused-argument
        """
        Navigate to the management menu.

        Args:
            handler: The handler from which this handler was called.
            kwargs: Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: Object with stored data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Management section. Choose the option:
        """
        )
        return HandlerResponse()

    def player_statistic(self, handler: Handler, **kwargs: KwArg) -> HandlerResponse:  # pylint: disable=unused-argument
        """
        Show statistics of past games.

        Args:
            handler: The handler from which this handler was called.
            kwargs: Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: Object with stored data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Past games statistics:
        """
        )
        self.service.show_past_games_statistic()

        return HandlerResponse()

    def ranking_table(self, handler: Handler, **kwargs: KwArg) -> HandlerResponse:  # pylint: disable=unused-argument
        """
        Show the ranking table.

        Args:
            handler: The handler from which this handler was called.
            kwargs: Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: Object with stored data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Ranking table:
        """
        )
        self.service.show_ranking_table()

        return HandlerResponse()

    def exit_game(self, handler: Handler, **kwargs: KwArg) -> None:  # pylint: disable=unused-argument
        """
        Exit the game.

        Args:
            handler: The handler from which this handler was called.
            kwargs: Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: Object with stored data to run the next handlers or generated dynamic handlers.
        """
        print(
            """
        Bue, see you next time!
        """
        )
        delete_session(self.db_session)
        sys.exit(0)
