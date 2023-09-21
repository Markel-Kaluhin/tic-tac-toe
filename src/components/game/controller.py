from mypy_extensions import KwArg
from sqlalchemy.orm import Session

from src.components.game.service import GameService
from src.components.model import BaseController
from src.handler.model import HandlerResponse, Handler


class Game(BaseController):
    """
    Controller for the game functionalities.

    Attributes:
        db_session (Any): The database session.
        service (GameService): Instance of the GameService.

    Methods:
        __init__(self, db_session):
            Initializes a Game instance.
        start_game(self, handler, **kwargs):
            Launches the game.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Initializes a Game instance.

        Args:
            db_session (Any): The database session.
        """
        self.db_session = db_session
        self.service = GameService(self.db_session)

    def start_game(self, handler: Handler, **kwargs: KwArg) -> HandlerResponse:
        """
        Launches the game.

        Args:
            handler: The handler from which this handler was called.
            kwargs: Specific parameters passed from the previous handler.

        Returns:
            HandlerResponse: Object with stored data to run the next handlers or generated dynamic handlers.
        """

        self.service.start_game()

        return HandlerResponse()
