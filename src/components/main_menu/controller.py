from src.handler import HandlerResponse
from src.components.model import BaseController
from src.database import delete_session

from src.components.main_menu.service import MainMenuService


class MainMenu(BaseController):
    def __init__(self, db_session):
        self.db_session = db_session
        self.service = MainMenuService(self.db_session)

    def welcome(self, handler, **kwargs):
        """
        Welcome window, shown when the application is initialized

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Greeting player. Choose the option:
        ''')
        return HandlerResponse()

    def management(self, handler, **kwargs):
        """
        This handler is needed to go to the management menu

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Management section. Choose the option:
        ''')
        return HandlerResponse()

    def player_statistic(self, handler, **kwargs):
        """
        To show statistics of past games, who is against whom and who won

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Past games statistics:
        ''')
        self.service.show_past_games_statistic()

        return HandlerResponse()

    def ranking_table(self, handler, **kwargs):
        """
        Used to call the ranking table

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Ranking table:
        ''')
        self.service.show_ranking_table()

        return HandlerResponse()

    def exit_game(self, handler, **kwargs):
        """
        Pretty obvious, but with this point you are leaving the game

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Bue, see you next time!
        ''')
        delete_session(self.db_session)
        exit(0)
        return HandlerResponse()
