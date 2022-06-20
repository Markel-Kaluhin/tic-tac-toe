from src.handler import HandlerResponse
from src.components.model import BaseController

from src.components.game.service import GameService


class Game(BaseController):
    def __init__(self, db_session):
        self.db_session = db_session
        self.service = GameService(self.db_session)

    def start_game(self, handler, **kwargs):
        """
        This handler launches the game

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """

        self.service.start_game()

        return HandlerResponse()
