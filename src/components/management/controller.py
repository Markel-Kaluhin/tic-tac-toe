from src.database.model.user import User
from src.handler import HandlerResponse
from src.components.model import BaseController

from src.components.management.service import ManagementService


class Management(BaseController):
    def __init__(self, db_session):
        self.db_session = db_session
        self.service = ManagementService(self.db_session)

    def player_details(self, handler, **kwargs):
        """
        Detailed information of one user. All empty fields will be visible
         as None

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """

        user: User = kwargs['user']

        self.service.show_player_details(user)

        return HandlerResponse()

    def player_list(self, handler, **kwargs):
        """
        A list of users in which you can select one to view detailed
         information

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Choose one to see detail.
        Player table:
        ''')

        result = self.service.show_player_list(handler, 'Management', 'player_details')

        return HandlerResponse(dynamic_menu_items=result)

    def player_create(self, handler, **kwargs):
        """
        This is where flow starts creating a user. If you do not enter
         a nickname, it will be created automatically

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """

        self.service.player_create()

        return HandlerResponse()

    def player_delete(self, handler, **kwargs):
        """
        A list of users in which you can select one to delete

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        print('''
        Choose one to delete.
        Player list:
        ''')

        result = self.service.show_player_list(handler, 'Management', 'player_delete_confirmation')

        return HandlerResponse(dynamic_menu_items=result)

    def player_delete_confirmation(self, handler, **kwargs):
        """
        Sometimes the finger can flinch, it is better to ask again before
         deleting the user

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        user: User = kwargs['user']

        decision = input('Are you sure? y/N')
        if decision == 'y':
            self.db_session.delete(user)
            self.db_session.commit()
            print(f'User {user.nickname} was deleted')
        return HandlerResponse()

    def new_league_season(self, handler, **kwargs):
        """
        A new season is created here.

        :param handler: The handler from which this handler was called
        :param kwargs: Specific parameters passed from the previous handler
        :return: HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """

        self.service.create_new_league_season()

        return HandlerResponse()
